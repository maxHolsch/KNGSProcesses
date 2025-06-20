# Email Progress Checker

A professional Electron application built with React for checking email progress status from Excel spreadsheets.

## Features

- **Excel File Upload**: Drag and drop or click to upload Excel files (.xlsx, .xls)
- **Smart Sheet Detection**: Automatically finds "in progress" sheets in your workbook
- **Professional Data View**: Interactive table with sorting, filtering, and search capabilities
- **Employee Progress Checker**: Filter and search employees to check their individual progress
- **Modern UI**: Beautiful, responsive interface with professional styling
- **Fast Performance**: Efficient data processing and rendering

## Prerequisites

Before running this application, make sure you have:

- **Node.js** (version 14 or higher)
- **npm** (usually comes with Node.js)

## Installation

1. **Clone or download this project** to your local machine

2. **Open terminal/command prompt** in the project directory

3. **Install dependencies**:
   ```bash
   npm install
   ```

## Running the Application

### Development Mode (Recommended)

To run the app in development mode with hot reloading:

```bash
npm run dev
```

This will:
- Start the React development server on `http://localhost:3000`
- Open the Electron app automatically
- Allow for real-time code changes

### Production Mode

To run the app in production mode:

1. **Build the React app**:
   ```bash
   npm run react-build
   ```

2. **Start the Electron app**:
   ```bash
   npm start
   ```

## How to Use

### 1. Upload Excel File

1. Launch the application
2. On the main screen, either:
   - Click the upload area to select a file
   - Drag and drop an Excel file (.xlsx or .xls) onto the upload area

### 2. Excel File Requirements

Your Excel file must have:
- A sheet named **"in progress"** (case insensitive)
- **Column A**: Ticket numbers
- **Column F**: Employee names

### 3. View Data

After uploading, you can:
- **View Data**: See a professional, interactive table of your Excel data
- **Search and Filter**: Use the search box to find specific records
- **Sort Columns**: Click column headers to sort data
- **View Statistics**: See summary statistics about your data

### 4. Check Employee Progress

- Navigate to the **"Check Progress"** tab
- Type an employee name to filter the dropdown
- Select an employee from the filtered list
- Click **"Check Progress"** to see their detailed records

## File Structure

```
email-progress-checker/
├── main.js                 # Electron main process
├── package.json           # Dependencies and scripts
├── public/
│   └── index.html        # HTML template
├── src/
│   ├── App.js            # Main React component
│   ├── App.css           # App-specific styles
│   ├── index.js          # React entry point
│   ├── index.css         # Global styles
│   └── components/
│       ├── FileUpload.js    # File upload component
│       ├── DataView.js      # Data display component
│       └── EmployeeSelector.js # Employee selection component
└── README.md             # This file
```

## Features in Detail

### Data View
- **Interactive Table**: Professional table with hover effects and highlighting
- **Column Sorting**: Click any column header to sort ascending or descending
- **Global Search**: Search across all columns simultaneously
- **Statistics**: View total records, unique employees, and unique tickets
- **Column Highlighting**: Ticket numbers (Column A) and employee names (Column F) are highlighted

### Employee Selector
- **Smart Search**: Type to filter employee names in real-time
- **Progress Reports**: Detailed view of all records for selected employee
- **Quick Selection**: Click employee names from the summary to select them
- **Statistics**: See totals and unique counts for the selected employee

### Professional Styling
- **Modern Design**: Clean, professional interface
- **Responsive Layout**: Works on different screen sizes
- **Smooth Animations**: Hover effects and transitions
- **Color Coding**: Different colors for different data types
- **Professional Typography**: Clear, readable fonts

## Building for Distribution

To create a distributable version of the app:

```bash
npm run build
```

This will create platform-specific installers in the `dist/` folder.

## Troubleshooting

### Common Issues

1. **"No 'in progress' sheet found"**
   - Ensure your Excel file has a sheet named "in progress" (case doesn't matter)
   - Check that the sheet name doesn't have extra spaces

2. **"Empty sheet" error**
   - Make sure your "in progress" sheet has data
   - Ensure Column A has ticket numbers and Column F has employee names

3. **App won't start**
   - Make sure you ran `npm install` first
   - Check that Node.js is properly installed
   - Try deleting `node_modules` folder and running `npm install` again

### Getting Help

If you encounter issues:
1. Check the console for error messages (View → Toggle Developer Tools)
2. Ensure your Excel file format matches the requirements
3. Try with a different Excel file to isolate the issue

## Technical Details

- **Frontend**: React 18 with functional components and hooks
- **Desktop Framework**: Electron 22
- **Excel Processing**: SheetJS (xlsx library)
- **Routing**: React Router v6
- **Styling**: CSS3 with modern features
- **Build System**: Create React App with Electron integration

## License

MIT License - feel free to use and modify as needed.

---

**Happy Progress Checking!** 