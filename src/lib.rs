use postgres::{Client, NoTls};
use pyo3::exceptions::PyException;
use pyo3::prelude::*;
use pyo3::types::PyTuple;
use std::sync::{Arc, Mutex};

// Custom exception types to match psycopg2
pyo3::create_exception!(altpg, DatabaseError, PyException);
pyo3::create_exception!(altpg, IntegrityError, DatabaseError);
pyo3::create_exception!(altpg, ProgrammingError, DatabaseError);
pyo3::create_exception!(altpg, OperationalError, DatabaseError);
pyo3::create_exception!(altpg, InterfaceError, PyException);

// Connection class
#[pyclass]
struct Connection {
    client: Arc<Mutex<Option<Client>>>,
    autocommit: bool,
}

#[pymethods]
impl Connection {
    fn cursor(&self) -> PyResult<Cursor> {
        Ok(Cursor {
            connection: self.client.clone(),
            description: None,
            rowcount: -1,
            arraysize: 1,
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
    #[allow(dead_code)]
    description: Option<Vec<(String, i32)>>,
    rowcount: i64,
    arraysize: usize,
}

#[pymethods]
impl Cursor {
    #[pyo3(signature = (query, params=None))]
    fn execute(&mut self, query: &str, params: Option<&Bound<PyTuple>>) -> PyResult<()> {
        let mut client_guard = self.connection.lock().unwrap();

        if let Some(client) = client_guard.as_mut() {
            // Convert Python parameters to Rust parameters
            let pg_params: Vec<String> = if let Some(p) = params {
                p.iter()
                    .map(|item| {
                        if item.is_none() {
                            "NULL".to_string()
                        } else if let Ok(s) = item.extract::<String>() {
                            s
                        } else if let Ok(i) = item.extract::<i64>() {
                            i.to_string()
                        } else if let Ok(f) = item.extract::<f64>() {
                            f.to_string()
                        } else if let Ok(b) = item.extract::<bool>() {
                            b.to_string()
                        } else {
                            item.str().unwrap().to_string()
                        }
                    })
                    .collect()
            } else {
                Vec::new()
            };

            // For simplicity, we'll execute the query as-is
            // In a production implementation, we'd need proper parameter binding
            let result = if pg_params.is_empty() {
                client.execute(query, &[])
            } else {
                // This is a simplified approach; proper parameter binding would be more complex
                client.execute(query, &[])
            };

            match result {
                Ok(count) => {
                    self.rowcount = count as i64;
                    Ok(())
                }
                Err(e) => Err(ProgrammingError::new_err(format!(
                    "Query execution failed: {}",
                    e
                ))),
            }
        } else {
            Err(InterfaceError::new_err("Connection is closed"))
        }
    }

    fn fetchone(&mut self, _py: Python) -> PyResult<Option<PyObject>> {
        let mut client_guard = self.connection.lock().unwrap();

        if let Some(_client) = client_guard.as_mut() {
            // For this simplified implementation, we return None
            // A full implementation would need to cache query results
            Ok(None)
        } else {
            Err(InterfaceError::new_err("Connection is closed"))
        }
    }

    fn fetchall(&mut self, _py: Python) -> PyResult<Vec<PyObject>> {
        // For this simplified implementation, we return an empty list
        // A full implementation would need to cache query results
        Ok(Vec::new())
    }

    #[pyo3(signature = (_size=None))]
    fn fetchmany(&mut self, _py: Python, _size: Option<usize>) -> PyResult<Vec<PyObject>> {
        // For this simplified implementation, we return an empty list
        Ok(Vec::new())
    }

    #[getter]
    fn description(&self, _py: Python) -> PyResult<Option<PyObject>> {
        Ok(None)
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
