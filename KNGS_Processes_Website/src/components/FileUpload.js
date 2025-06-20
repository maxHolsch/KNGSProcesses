import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import * as XLSX from 'xlsx';
import { Upload, FileSpreadsheet, BarChart3, FileText } from 'lucide-react';

const FileUpload = ({ onDataLoad, hasData }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [isDragOver, setIsDragOver] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [processingStep, setProcessingStep] = useState('');
  const fileInputRef = useRef(null);
  const navigate = useNavigate();

  const handleFileUpload = async (file) => {
    if (!file) return;

    console.log('Starting file upload process...', file);
    setProcessingStep('Validating file...');

    // Check if file is Excel format
    if (!file.name.match(/\.(xlsx|xls)$/)) {
      setError('Please upload a valid Excel file (.xlsx or .xls)');
      return;
    }

    setIsLoading(true);
    setError('');
    setUploadSuccess(false);

    const timeoutId = setTimeout(() => {
      console.error('File processing timeout');
      setError('File processing timeout. Please try with a smaller file or check the file format.');
      setIsLoading(false);
      setProcessingStep('');
    }, 30000);

    try {
      setProcessingStep('Reading file...');
      const reader = new FileReader();
      
      reader.onload = (e) => {
        try {
          clearTimeout(timeoutId);
          setProcessingStep('Parsing Excel data...');
          const data = new Uint8Array(e.target.result);
          const workbook = XLSX.read(data, { type: 'array' });
          
          setProcessingStep('Looking for "in progress" sheet...');
          const inProgressSheet = workbook.SheetNames.find(name => 
            name.toLowerCase().includes('in progress') || name.toLowerCase().includes('inprogress')
          );

          if (!inProgressSheet) {
            setError(`No "in progress" sheet found. Available sheets: ${workbook.SheetNames.join(', ')}`);
            setIsLoading(false);
            setProcessingStep('');
            return;
          }

          setProcessingStep('Processing sheet data...');
          const worksheet = workbook.Sheets[inProgressSheet];
          
          // Extract merged cells information
          const merges = worksheet['!merges'] || [];
          
          const range = XLSX.utils.decode_range(worksheet['!ref'] || 'A1:A1');
          let maxRow = 0;
          let maxCol = 0;
          const scanLimit = Math.min(range.e.r, 5000);
          const colLimit = Math.min(range.e.c, 50);
          
          setProcessingStep('Detecting actual data range...');
          for (let row = 0; row <= scanLimit; row++) {
            for (let col = 0; col <= colLimit; col++) {
              const cellAddress = XLSX.utils.encode_cell({ r: row, c: col });
              if (worksheet[cellAddress] && worksheet[cellAddress].v) {
                maxRow = Math.max(maxRow, row);
                maxCol = Math.max(maxCol, col);
              }
            }
          }
          
          const actualRange = `A1:${XLSX.utils.encode_cell({ r: maxRow, c: Math.max(maxCol, 6) })}`;
          setProcessingStep('Converting to JSON...');
          
          const jsonData = XLSX.utils.sheet_to_json(worksheet, { 
            header: 1, range: actualRange, defval: ''
          });

          if (jsonData.length <= 1) { // Only headers or empty
            setError('The "in progress" sheet appears to be empty or contains no data.');
            setIsLoading(false);
            setProcessingStep('');
            return;
          }

          setProcessingStep('Processing Excel headers...');
          // Handle two-row header structure
          const headerRow1 = jsonData[0] || []; // "General Information" etc.
          const headerRow2 = jsonData[1] || []; // "Ticket #", "Workforce", etc.
          
          // Create merged header structure
          const mergedHeaders = [];
          const subHeaders = [];
          
          // Process merged cells for row 1 (main headers like "General Information")
          const processedRow1 = [...headerRow1];
          merges.forEach(merge => {
            if (merge.s.r === 0) { // Row 1 merges
              const mergedValue = headerRow1[merge.s.c] || '';
              if (mergedValue.trim()) {
                // Only set the value in the first column of the merge
                processedRow1[merge.s.c] = mergedValue;
                // Clear other columns in the merge
                for (let col = merge.s.c + 1; col <= merge.e.c; col++) {
                  processedRow1[col] = '';
                }
              }
            }
          });
          
          // Combine both header rows into a structure
          for (let i = 0; i < Math.max(processedRow1.length, headerRow2.length); i++) {
            mergedHeaders[i] = processedRow1[i] || '';
            subHeaders[i] = headerRow2[i] || '';
          }

          setProcessingStep('Extracting employee data...');
          const employees = [];
          const processedData = jsonData.slice(2).map(row => row); // Skip both header rows

          jsonData.slice(2).forEach((row, index) => {
            if (!row || row.length === 0) return;
            const ticketNumber = row[0];
            const employeeName = row[5];
            if (ticketNumber && employeeName) {
              const ticketStr = ticketNumber.toString().trim();
              const nameStr = employeeName.toString().trim();
              if (ticketStr && nameStr) {
                employees.push({ name: nameStr, ticketNumber: ticketStr, rowIndex: index + 2 });
              }
            }
          });

          if (employees.length === 0) {
            setError('No valid data found. Check columns A (ticket #) and F (employee name).');
            setIsLoading(false);
            setProcessingStep('');
            return;
          }

          setProcessingStep('Removing duplicates...');
          const uniqueEmployees = employees.filter((employee, index, self) =>
            index === self.findIndex(e => e.name.toLowerCase() === employee.name.toLowerCase())
          );

          setProcessingStep('Finalizing data...');
          const fullData = {
            sheetName: inProgressSheet,
            headers: subHeaders, // Use row 2 as main headers
            mergedHeaders: mergedHeaders, // Row 1 merged headers
            rows: processedData,
          };

          onDataLoad(fullData, uniqueEmployees);
          setUploadSuccess(true);
          setIsLoading(false);
          setProcessingStep('');

          setTimeout(() => navigate('/data-view'), 1000);

        } catch (parseError) {
          clearTimeout(timeoutId);
          console.error('Error parsing Excel file:', parseError);
          setError(`Error parsing Excel file: ${parseError.message}.`);
          setIsLoading(false);
          setProcessingStep('');
        }
      };
      reader.onerror = (error) => {
        clearTimeout(timeoutId);
        console.error('FileReader error:', error);
        setError('Error reading file. Please try again.');
        setIsLoading(false);
        setProcessingStep('');
      };
      reader.readAsArrayBuffer(file);
    } catch (error) {
      clearTimeout(timeoutId);
      console.error('Error in file upload process:', error);
      setError(`Error uploading file: ${error.message}.`);
      setIsLoading(false);
      setProcessingStep('');
    }
  };

  const handleDragEvents = (e, isOver) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(isOver);
  };

  const handleDrop = (e) => {
    handleDragEvents(e, false);
    const files = e.dataTransfer.files;
    if (files.length > 0) handleFileUpload(files[0]);
  };

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) handleFileUpload(file);
  };

  return (
    <>
      <div className="page-header" style={{textAlign: 'left', marginBottom: '16px'}}>
        <h1 className="page-title" style={{fontSize: '2rem'}}>
          File Upload
        </h1>
        <p className="page-subtitle" style={{fontSize: '1rem', color: 'var(--kn-text-secondary)'}}>
          Upload your Excel file to begin checking email progress.
        </p>
      </div>

      {error && (
        <div className="error">
          <strong>Error:</strong> {error}
          <br />
          <small>Check the console (F12) for more details.</small>
        </div>
      )}

      {uploadSuccess && (
        <div className="success">
          <strong>Success!</strong> File uploaded successfully. Redirecting...
        </div>
      )}

      <div className="card">
        <div
          className={`upload-area ${isDragOver ? 'drag-over' : ''}`}
          onDragOver={(e) => handleDragEvents(e, true)}
          onDragLeave={(e) => handleDragEvents(e, false)}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <input
            type="file"
            ref={fileInputRef}
            accept=".xlsx,.xls"
            onChange={handleFileSelect}
            style={{ display: 'none' }}
          />
          
          {isLoading ? (
            <div className="loading">
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <BarChart3 size={20} style={{ color: 'var(--kn-blue)' }} />
                Processing...
              </div>
              {processingStep && <div style={{ fontSize: '14px', marginTop: '10px' }}>{processingStep}</div>}
            </div>
          ) : (
            <>
              <div className="upload-icon">
                <Upload size={48} style={{ color: 'var(--kn-blue)' }} />
              </div>
              <div className="upload-text">
                {hasData ? 'Upload a New File' : 'Drag & Drop or Click to Upload'}
              </div>
              <div className="upload-subtext">
                Supported formats: .xlsx, .xls
              </div>
            </>
          )}
        </div>
      </div>

      <div className="card">
        <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--kn-blue)' }}>
          <FileText size={20} />
          Instructions
        </h3>
        <ul style={{ listStylePosition: 'inside', marginTop: '15px', color: 'var(--kn-text-secondary)' }}>
          <li>Your Excel file must contain a sheet named "in progress".</li>
          <li>Column <strong>A</strong> should contain ticket numbers.</li>
          <li>Column <strong>F</strong> should contain employee names.</li>
          <li>The application will read and process this data for you.</li>
        </ul>
      </div>
    </>
  );
};

export default FileUpload; 