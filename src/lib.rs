use postgres::{Client, NoTls, Row};
use pyo3::exceptions::PyException;
use pyo3::prelude::*;
use pyo3::types::{PyTuple, PyList};
use std::sync::{Arc, Mutex};
use serde_json::Value as JsonValue;

// Custom exception types to match psycopg2
pyo3::create_exception!(altpg, DatabaseError, PyException);
pyo3::create_exception!(altpg, IntegrityError, DatabaseError);
pyo3::create_exception!(altpg, ProgrammingError, DatabaseError);
pyo3::create_exception!(altpg, OperationalError, DatabaseError);
pyo3::create_exception!(altpg, InterfaceError, PyException);

// Helper function to convert PostgreSQL Row to Python tuple
fn row_to_python(py: Python, row: &Row) -> PyResult<PyObject> {
    let tuple = PyTuple::new_bound(py, 
        (0..row.len()).map(|i| {
            // Try different types in order
            if let Ok(val) = row.try_get::<_, Option<String>>(i) {
                val.to_object(py)
            } else if let Ok(val) = row.try_get::<_, Option<i32>>(i) {
                val.to_object(py)
            } else if let Ok(val) = row.try_get::<_, Option<i64>>(i) {
                val.to_object(py)
            } else if let Ok(val) = row.try_get::<_, Option<f64>>(i) {
                val.to_object(py)
            } else if let Ok(val) = row.try_get::<_, Option<bool>>(i) {
                val.to_object(py)
            } else if let Ok(val) = row.try_get::<_, Option<Vec<u8>>>(i) {
                val.to_object(py)
            } else if let Ok(val) = row.try_get::<_, Option<JsonValue>>(i) {
                match val {
                    Some(json) => json.to_string().to_object(py),
                    None => py.None(),
                }
            } else {
                // Return None for unsupported types
                py.None()
            }
        })
    );
    Ok(tuple.into())
}

// Connection class
#[pyclass]
struct Connection {
    client: Arc<Mutex<Option<Client>>>,
    autocommit: bool,
}

#[pymethods]
impl Connection {
    #[pyo3(signature = (name=None))]
    fn cursor(&self, name: Option<&str>) -> PyResult<Cursor> {
        Ok(Cursor {
            connection: self.client.clone(),
            description: None,
            rowcount: -1,
            arraysize: 1,
            cached_rows: Vec::new(),
            current_position: 0,
            cursor_name: name.map(|s| s.to_string()),
        })
    }

    fn commit(&self) -> PyResult<()> {
        let mut client_guard = self.client.lock().unwrap();
        if let Some(client) = client_guard.as_mut() {
            client
                .execute("COMMIT", &[])
                .map_err(|e| OperationalError::new_err(format!("Commit failed: {}", e)))?;
            // Start a new transaction
            client
                .execute("BEGIN", &[])
                .map_err(|e| OperationalError::new_err(format!("Begin failed: {}", e)))?;
            Ok(())
        } else {
            Err(InterfaceError::new_err("Connection is closed"))
        }
    }

    fn rollback(&self) -> PyResult<()> {
        let mut client_guard = self.client.lock().unwrap();
        if let Some(client) = client_guard.as_mut() {
            client
                .execute("ROLLBACK", &[])
                .map_err(|e| OperationalError::new_err(format!("Rollback failed: {}", e)))?;
            // Start a new transaction
            client
                .execute("BEGIN", &[])
                .map_err(|e| OperationalError::new_err(format!("Begin failed: {}", e)))?;
            Ok(())
        } else {
            Err(InterfaceError::new_err("Connection is closed"))
        }
    }

    fn close(&self) -> PyResult<()> {
        let mut client_guard = self.client.lock().unwrap();
        *client_guard = None;
        Ok(())
    }

    #[getter]
    fn autocommit(&self) -> bool {
        self.autocommit
    }

    #[setter]
    fn set_autocommit(&mut self, value: bool) {
        self.autocommit = value;
    }

    fn __enter__(slf: PyRef<Self>) -> PyRef<Self> {
        slf
    }

    #[pyo3(signature = (_exc_type=None, _exc_val=None, _exc_tb=None))]
    fn __exit__(
        &self,
        _exc_type: Option<&Bound<PyAny>>,
        _exc_val: Option<&Bound<PyAny>>,
        _exc_tb: Option<&Bound<PyAny>>,
    ) -> PyResult<bool> {
        self.close()?;
        Ok(false)
    }
}

// Cursor class
#[pyclass]
struct Cursor {
    connection: Arc<Mutex<Option<Client>>>,
    description: Option<Vec<(String, i32)>>,
    rowcount: i64,
    arraysize: usize,
    cached_rows: Vec<PyObject>,
    current_position: usize,
    cursor_name: Option<String>,
}

#[pymethods]
impl Cursor {
    #[pyo3(signature = (query, _params=None))]
    fn execute(&mut self, py: Python, query: &str, _params: Option<&Bound<PyTuple>>) -> PyResult<()> {
        // Clear previous results
        self.cached_rows.clear();
        self.current_position = 0;
        self.description = None;
        
        let mut client_guard = self.connection.lock().unwrap();

        if let Some(client) = client_guard.as_mut() {
            // For queries that return results, use query() instead of execute()
            let query_lower = query.trim().to_lowercase();
            
            if query_lower.starts_with("select") || 
               query_lower.starts_with("with") ||
               query_lower.starts_with("returning") {
                // This is a SELECT query - use query() to get results
                match client.query(query, &[]) {
                    Ok(rows) => {
                        self.rowcount = rows.len() as i64;
                        
                        // Store column descriptions
                        if !rows.is_empty() {
                            let first_row = &rows[0];
                            let mut desc = Vec::new();
                            for col in first_row.columns() {
                                desc.push((col.name().to_string(), 0));
                            }
                            self.description = Some(desc);
                        }
                        
                        // Cache all rows
                        for row in &rows {
                            self.cached_rows.push(row_to_python(py, row)?);
                        }
                        Ok(())
                    }
                    Err(e) => Err(ProgrammingError::new_err(format!(
                        "Query execution failed: {}",
                        e
                    ))),
                }
            } else {
                // This is an INSERT, UPDATE, DELETE, etc. - use execute()
                match client.execute(query, &[]) {
                    Ok(count) => {
                        self.rowcount = count as i64;
                        Ok(())
                    }
                    Err(e) => Err(ProgrammingError::new_err(format!(
                        "Query execution failed: {}",
                        e
                    ))),
                }
            }
        } else {
            Err(InterfaceError::new_err("Connection is closed"))
        }
    }

    fn fetchone(&mut self, py: Python) -> PyResult<Option<PyObject>> {
        if self.current_position < self.cached_rows.len() {
            let row = self.cached_rows[self.current_position].clone_ref(py);
            self.current_position += 1;
            Ok(Some(row))
        } else {
            Ok(None)
        }
    }

    fn fetchall(&mut self, py: Python) -> PyResult<Vec<PyObject>> {
        let result: Vec<PyObject> = self.cached_rows[self.current_position..].iter()
            .map(|obj| obj.clone_ref(py))
            .collect();
        self.current_position = self.cached_rows.len();
        Ok(result)
    }

    #[pyo3(signature = (size=None))]
    fn fetchmany(&mut self, py: Python, size: Option<usize>) -> PyResult<Vec<PyObject>> {
        let fetch_size = size.unwrap_or(self.arraysize);
        let end = std::cmp::min(self.current_position + fetch_size, self.cached_rows.len());
        let result: Vec<PyObject> = self.cached_rows[self.current_position..end].iter()
            .map(|obj| obj.clone_ref(py))
            .collect();
        self.current_position = end;
        Ok(result)
    }

    #[getter]
    fn description(&self, py: Python) -> PyResult<Option<PyObject>> {
        if let Some(desc) = &self.description {
            let list = PyList::empty_bound(py);
            for (name, type_code) in desc {
                let tuple = PyTuple::new_bound(py, &[
                    name.to_object(py),
                    type_code.to_object(py),
                    py.None(),  // display_size
                    py.None(),  // internal_size
                    py.None(),  // precision
                    py.None(),  // scale
                    py.None(),  // null_ok
                ]);
                list.append(tuple)?;
            }
            Ok(Some(list.into()))
        } else {
            Ok(None)
        }
    }

    #[getter]
    fn rowcount(&self) -> i64 {
        self.rowcount
    }

    #[getter]
    fn arraysize(&self) -> usize {
        self.arraysize
    }

    #[setter]
    fn set_arraysize(&mut self, value: usize) {
        self.arraysize = value;
    }

    fn close(&self) -> PyResult<()> {
        Ok(())
    }

    fn __enter__(slf: PyRef<Self>) -> PyRef<Self> {
        slf
    }

    #[pyo3(signature = (_exc_type=None, _exc_val=None, _exc_tb=None))]
    fn __exit__(
        &self,
        _exc_type: Option<&Bound<PyAny>>,
        _exc_val: Option<&Bound<PyAny>>,
        _exc_tb: Option<&Bound<PyAny>>,
    ) -> PyResult<bool> {
        self.close()?;
        Ok(false)
    }

    fn __iter__(slf: PyRef<Self>) -> PyRef<Self> {
        slf
    }

    fn __next__(&mut self, py: Python) -> PyResult<Option<PyObject>> {
        self.fetchone(py)
    }
}

// Connect function
#[pyfunction]
#[pyo3(signature = (dsn=None, host=None, port=None, user=None, password=None, dbname=None))]
fn connect(
    dsn: Option<&str>,
    host: Option<&str>,
    port: Option<u16>,
    user: Option<&str>,
    password: Option<&str>,
    dbname: Option<&str>,
) -> PyResult<Connection> {
    let connection_string = if let Some(dsn_str) = dsn {
        dsn_str.to_string()
    } else {
        // Build connection string from individual parameters
        let host = host.unwrap_or("localhost");
        let port = port.unwrap_or(5432);
        let user = user.unwrap_or("postgres");
        let password = password.unwrap_or("");
        let dbname = dbname.unwrap_or("postgres");

        format!(
            "host={} port={} user={} password={} dbname={}",
            host, port, user, password, dbname
        )
    };

    match Client::connect(&connection_string, NoTls) {
        Ok(mut client) => {
            // Start a transaction by default
            client.execute("BEGIN", &[]).map_err(|e| {
                OperationalError::new_err(format!("Failed to start transaction: {}", e))
            })?;

            Ok(Connection {
                client: Arc::new(Mutex::new(Some(client))),
                autocommit: false,
            })
        }
        Err(e) => Err(OperationalError::new_err(format!(
            "Failed to connect to database: {}",
            e
        ))),
    }
}

// Connection Pool for managing multiple connections
#[pyclass]
struct ConnectionPool {
    connection_string: String,
    min_size: usize,
    max_size: usize,
    available: Arc<Mutex<Vec<Client>>>,
    in_use: Arc<Mutex<usize>>,
}

#[pymethods]
impl ConnectionPool {
    #[new]
    #[pyo3(signature = (dsn=None, host=None, port=None, user=None, password=None, dbname=None, min_size=1, max_size=10))]
    fn new(
        dsn: Option<&str>,
        host: Option<&str>,
        port: Option<u16>,
        user: Option<&str>,
        password: Option<&str>,
        dbname: Option<&str>,
        min_size: usize,
        max_size: usize,
    ) -> PyResult<Self> {
        let connection_string = if let Some(dsn_str) = dsn {
            dsn_str.to_string()
        } else {
            let host = host.unwrap_or("localhost");
            let port = port.unwrap_or(5432);
            let user = user.unwrap_or("postgres");
            let password = password.unwrap_or("");
            let dbname = dbname.unwrap_or("postgres");
            format!(
                "host={} port={} user={} password={} dbname={}",
                host, port, user, password, dbname
            )
        };

        // Create initial pool of connections
        let mut clients = Vec::new();
        for _ in 0..min_size {
            match Client::connect(&connection_string, NoTls) {
                Ok(mut client) => {
                    client.execute("BEGIN", &[]).map_err(|e| {
                        OperationalError::new_err(format!("Failed to start transaction: {}", e))
                    })?;
                    clients.push(client);
                }
                Err(e) => {
                    return Err(OperationalError::new_err(format!(
                        "Failed to create connection pool: {}",
                        e
                    )))
                }
            }
        }

        Ok(ConnectionPool {
            connection_string,
            min_size,
            max_size,
            available: Arc::new(Mutex::new(clients)),
            in_use: Arc::new(Mutex::new(0)),
        })
    }

    fn get_connection(&self) -> PyResult<Connection> {
        let mut available = self.available.lock().unwrap();
        let mut in_use = self.in_use.lock().unwrap();

        if let Some(client) = available.pop() {
            *in_use += 1;
            Ok(Connection {
                client: Arc::new(Mutex::new(Some(client))),
                autocommit: false,
            })
        } else if *in_use < self.max_size {
            // Create a new connection if we haven't reached max_size
            match Client::connect(&self.connection_string, NoTls) {
                Ok(mut client) => {
                    client.execute("BEGIN", &[]).map_err(|e| {
                        OperationalError::new_err(format!("Failed to start transaction: {}", e))
                    })?;
                    *in_use += 1;
                    Ok(Connection {
                        client: Arc::new(Mutex::new(Some(client))),
                        autocommit: false,
                    })
                }
                Err(e) => Err(OperationalError::new_err(format!(
                    "Failed to create connection: {}",
                    e
                ))),
            }
        } else {
            Err(OperationalError::new_err(
                "Connection pool exhausted. All connections are in use.",
            ))
        }
    }

    fn close_all(&self) -> PyResult<()> {
        let mut available = self.available.lock().unwrap();
        available.clear();
        Ok(())
    }

    fn __enter__(slf: PyRef<Self>) -> PyRef<Self> {
        slf
    }

    #[pyo3(signature = (_exc_type=None, _exc_val=None, _exc_tb=None))]
    fn __exit__(
        &self,
        _exc_type: Option<&Bound<PyAny>>,
        _exc_val: Option<&Bound<PyAny>>,
        _exc_tb: Option<&Bound<PyAny>>,
    ) -> PyResult<bool> {
        self.close_all()?;
        Ok(false)
    }
}

// DB-API 2.0 module-level attributes
#[pyfunction]
fn apilevel() -> &'static str {
    "2.0"
}

#[pyfunction]
fn threadsafety() -> i32 {
    2 // Threads may share the module and connections
}

#[pyfunction]
fn paramstyle() -> &'static str {
    "pyformat" // Python extended format codes
}

// Module initialization
#[pymodule]
fn _altpg(py: Python, m: &Bound<PyModule>) -> PyResult<()> {
    m.add_class::<Connection>()?;
    m.add_class::<Cursor>()?;
    m.add_class::<ConnectionPool>()?;
    m.add_function(wrap_pyfunction!(connect, m)?)?;
    m.add_function(wrap_pyfunction!(apilevel, m)?)?;
    m.add_function(wrap_pyfunction!(threadsafety, m)?)?;
    m.add_function(wrap_pyfunction!(paramstyle, m)?)?;

    // Add exception classes
    m.add("DatabaseError", py.get_type_bound::<DatabaseError>())?;
    m.add("IntegrityError", py.get_type_bound::<IntegrityError>())?;
    m.add("ProgrammingError", py.get_type_bound::<ProgrammingError>())?;
    m.add("OperationalError", py.get_type_bound::<OperationalError>())?;
    m.add("InterfaceError", py.get_type_bound::<InterfaceError>())?;

    Ok(())
}
