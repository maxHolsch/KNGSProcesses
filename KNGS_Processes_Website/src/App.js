import React, { useState } from 'react';
import { Routes, Route, NavLink, useLocation } from 'react-router-dom';
import FileUpload from './components/FileUpload';
import DataView from './components/DataView';
import EmployeeSelector from './components/EmployeeSelector';
import './App.css';

// A simple, generic logo component
const Logo = () => (
  <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M12 2L2 7V17L12 22L22 17V7L12 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    <path d="M2 7L12 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    <path d="M12 22V12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    <path d="M22 7L12 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    <path d="M17 4.5L7 9.5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
);

function App() {
  const [excelData, setExcelData] = useState(null);
  const [employees, setEmployees] = useState([]);
  const location = useLocation();

  const handleDataLoad = (data, employeeList) => {
    setExcelData(data);
    setEmployees(employeeList);
  };

  const handleReset = () => {
    setExcelData(null);
    setEmployees([]);
  }

  return (
    <div className="app">
      <nav className="navigation">
        <div className="nav-content">
          <h1 className="nav-title">
            <Logo />
            <span>Email Progress Checker</span>
          </h1>
          <div className="nav-links">
            <NavLink to="/" className="nav-link" onClick={handleReset}>
              Upload File
            </NavLink>
            {excelData && (
              <>
                <NavLink to="/data-view" className="nav-link">
                  View Data
                </NavLink>
                <NavLink to="/employee-check" className="nav-link">
                  Check Progress
                </NavLink>
              </>
            )}
          </div>
        </div>
      </nav>

      <main className="container">
        <Routes>
          <Route 
            path="/" 
            element={
              <FileUpload 
                onDataLoad={handleDataLoad} 
                hasData={!!excelData}
              />
            } 
          />
          <Route 
            path="/data-view" 
            element={
              excelData ? (
                <DataView data={excelData} />
              ) : (
                <div className="card" style={{textAlign: 'center'}}>
                  <h2>No data loaded</h2>
                  <p style={{margin: '16px 0'}}>Please upload an Excel file first.</p>
                  <NavLink to="/" className="btn">
                    Go to Upload
                  </NavLink>
                </div>
              )
            } 
          />
          <Route 
            path="/employee-check" 
            element={
              employees.length > 0 ? (
                <EmployeeSelector 
                  employees={employees} 
                  excelData={excelData}
                />
              ) : (
                <div className="card" style={{textAlign: 'center'}}>
                   <h2>No data loaded</h2>
                  <p style={{margin: '16px 0'}}>Please upload an Excel file first.</p>
                  <NavLink to="/" className="btn">
                    Go to Upload
                  </NavLink>
                </div>
              )
            } 
          />
        </Routes>
      </main>
    </div>
  );
}

export default App; 