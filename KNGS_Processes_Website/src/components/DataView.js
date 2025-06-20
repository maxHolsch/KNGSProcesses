import React, { useState, useMemo } from 'react';
import { Search, ArrowUpDown, ChevronUp, ChevronDown } from 'lucide-react';

const DataView = ({ data }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [sortColumn, setSortColumn] = useState(null);
  const [sortDirection, setSortDirection] = useState('asc');

  // Filter and sort data
  const filteredAndSortedData = useMemo(() => {
    let filteredRows = data.rows.filter(row => {
      if (!searchTerm) return true;
      return row.some(cell => 
        cell && cell.toString().toLowerCase().includes(searchTerm.toLowerCase())
      );
    });

    if (sortColumn !== null) {
      filteredRows = [...filteredRows].sort((a, b) => {
        const aVal = a[sortColumn] || '';
        const bVal = b[sortColumn] || '';
        
        try {
          // Try numeric sort first
          const aNum = parseFloat(aVal);
          const bNum = parseFloat(bVal);
          if (!isNaN(aNum) && !isNaN(bNum)) {
            return sortDirection === 'asc' ? aNum - bNum : bNum - aNum;
          }
        } catch (e) { /* Fallback to localeCompare */ }
        
        // Fallback to string compare
        return sortDirection === 'asc' 
          ? aVal.toString().localeCompare(bVal.toString())
          : bVal.toString().localeCompare(aVal.toString());
      });
    }

    return filteredRows;
  }, [data.rows, searchTerm, sortColumn, sortDirection]);

  const handleSort = (columnIndex) => {
    if (sortColumn === columnIndex) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortColumn(columnIndex);
      setSortDirection('asc');
    }
  };

  const getSortIcon = (columnIndex) => {
    if (sortColumn !== columnIndex) return <ArrowUpDown size={14} style={{ color: 'var(--kn-text-secondary)' }} />;
    return sortDirection === 'asc' ? 
      <ChevronUp size={14} style={{ color: 'var(--kn-blue)' }} /> : 
      <ChevronDown size={14} style={{ color: 'var(--kn-blue)' }} />;
  };

  // Generate statistics
  const stats = useMemo(() => {
    const employeeNames = new Set(data.rows.map(row => row[5]).filter(Boolean));
    const ticketNumbers = new Set(data.rows.map(row => row[0]).filter(Boolean));

    return {
      totalRows: data.rows.length,
      uniqueEmployees: employeeNames.size,
      uniqueTickets: ticketNumbers.size,
      filteredRows: filteredAndSortedData.length
    };
  }, [data.rows, filteredAndSortedData.length]);

  const formatCellValue = (value) => {
    if (value === null || value === undefined) return '';
    // Basic date check (for Excel serial dates)
    if (typeof value === 'number' && value > 30000 && value < 80000) {
      try {
        const date = new Date((value - 25569) * 86400 * 1000);
        if(!isNaN(date)) return date.toLocaleDateString();
      } catch { /* Fallback to string */ }
    }
    return value.toString();
  };
  
  const getColumnLetter = (index) => String.fromCharCode(65 + index);

  return (
    <div className="data-view-container">
      <div className="page-header" style={{textAlign: 'left', marginBottom: '16px'}}>
        <h1 className="page-title" style={{fontSize: '2rem'}}>
          Data View: <span style={{color: 'var(--kn-blue)'}}>{data.sheetName}</span>
        </h1>
      </div>

      {/* Statistics Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Total Records</div>
          <div className="stat-number">{stats.totalRows}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Unique Employees</div>
          <div className="stat-number">{stats.uniqueEmployees}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Unique Tickets</div>
          <div className="stat-number">{stats.uniqueTickets}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Filtered Results</div>
          <div className="stat-number">{stats.filteredRows}</div>
        </div>
      </div>

      {/* Search and Controls */}
      <div className="card">
        <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px'}}>
          <div className="search-container" style={{flexGrow: 1, marginBottom: 0, minWidth: '300px'}}>
            <Search size={16} style={{position: 'absolute', left: '12px', top: '12px', color: 'var(--kn-text-secondary)'}} />
            <input
              type="text"
              placeholder="Search across all columns..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="employee-dropdown"
            />
          </div>
          <div style={{display: 'flex', gap: '10px', alignItems: 'center'}}>
            <span style={{color: 'var(--kn-text-secondary)', fontSize: '14px'}}>
              Showing {stats.filteredRows} of {stats.totalRows} records
            </span>
            <button 
              className="btn btn-secondary"
              onClick={() => {
                setSearchTerm('');
                setSortColumn(null);
              }}
            >
              Reset
            </button>
          </div>
        </div>
      </div>

      {/* Data Table */}
      <div className="table-container">
        <div className="scrollable-table">
          <table className="data-table">
            <thead>
              {/* First header row - merged headers like "General Information" */}
              {data.mergedHeaders && (
                <tr>
                  {data.mergedHeaders.map((header, index) => {
                    // Check if this is the start of a merged section
                    const isFirstInMerge = header && header.trim();
                    const nextHeaders = data.mergedHeaders.slice(index + 1);
                    const mergeLength = isFirstInMerge ? 
                      1 + nextHeaders.findIndex(h => h && h.trim() && h !== header) : 1;
                    const actualMergeLength = mergeLength === 0 ? 
                      nextHeaders.length + 1 : mergeLength;
                    
                    // Skip cells that are part of a previous merge
                    const isPreviousMerge = index > 0 && 
                      data.mergedHeaders.slice(0, index).some((prevHeader, prevIndex) => {
                        if (!prevHeader || !prevHeader.trim()) return false;
                        const prevMergeEnd = data.mergedHeaders.slice(prevIndex + 1)
                          .findIndex(h => h && h.trim() && h !== prevHeader);
                        const prevActualEnd = prevMergeEnd === -1 ? 
                          data.mergedHeaders.length - 1 : prevIndex + prevMergeEnd;
                        return index <= prevActualEnd;
                      });
                    
                    if (isPreviousMerge) return null;
                    
                    return (
                      <th 
                        key={index}
                        colSpan={isFirstInMerge ? actualMergeLength : 1}
                        style={{ 
                          textAlign: 'center',
                          backgroundColor: 'var(--kn-gray)',
                          borderBottom: '1px solid var(--kn-border-color)',
                          fontWeight: '700',
                          fontSize: '14px'
                        }}
                      >
                        {header || ''}
                      </th>
                    );
                  })}
                </tr>
              )}
              
              {/* Second header row - specific column names with light blue highlight */}
              <tr>
                {data.headers.map((header, index) => (
                  <th 
                    key={index}
                    onClick={() => handleSort(index)}
                    style={{ 
                      cursor: 'pointer', 
                      userSelect: 'none',
                      backgroundColor: 'var(--kn-light-blue)',
                      borderBottom: '2px solid var(--kn-border-color)'
                    }}
                    title={`Click to sort by ${header || `Column ${getColumnLetter(index)}`}`}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <span>
                        {header && header.trim() ? (
                          <>
                            <span style={{ 
                              fontSize: '12px', 
                              opacity: 0.7,
                              fontWeight: 'normal'
                            }}>
                              {getColumnLetter(index)}
                            </span>
                            <br />
                            <span style={{ fontWeight: '700' }}>
                              {header}
                            </span>
                          </>
                        ) : (
                          <span>
                            <strong>{getColumnLetter(index)}</strong>
                          </span>
                        )}
                      </span>
                      <span style={{ marginLeft: '8px', minWidth: '16px' }}>{getSortIcon(index)}</span>
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filteredAndSortedData.map((row, rowIndex) => (
                <tr key={rowIndex}>
                  {data.headers.map((_, colIndex) => (
                    <td 
                      key={colIndex}
                      style={{
                        backgroundColor: colIndex === 5 ? 'var(--kn-light-blue)' : undefined,
                        fontWeight: colIndex === 0 || colIndex === 5 ? '500' : 'normal'
                      }}
                      title={formatCellValue(row[colIndex])}
                    >
                      {formatCellValue(row[colIndex])}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {filteredAndSortedData.length === 0 && searchTerm && (
        <div className="card" style={{ textAlign: 'center', marginTop: '20px' }}>
          <h3>No Results Found</h3>
          <p>No records match your search term: "{searchTerm}"</p>
          <button className="btn" onClick={() => setSearchTerm('')}>
            Clear Search
          </button>
        </div>
      )}
    </div>
  );
};

export default DataView; 