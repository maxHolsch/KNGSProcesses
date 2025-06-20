import React, { useState, useMemo } from 'react';
import { 
  User, 
  BarChart3, 
  ZoomIn, 
  ZoomOut, 
  RotateCcw, 
  Maximize2, 
  Minimize2, 
  X, 
  Lightbulb,
  CheckCircle,
  XCircle,
  Clock,
  Mail,
  Paperclip,
  Copy,
  ExternalLink,
  Shield,
  Activity,
  AlertCircle
} from 'lucide-react';

const EmployeeSelector = ({ employees, excelData }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedEmployee, setSelectedEmployee] = useState(null);
  const [progressData, setProgressData] = useState(null);
  const [emailData, setEmailData] = useState(null);
  const [isLoadingEmails, setIsLoadingEmails] = useState(false);
  const [emailError, setEmailError] = useState('');
  const [emailServiceStatus, setEmailServiceStatus] = useState('unknown');
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [deviceCode, setDeviceCode] = useState('');
  const [authInProgress, setAuthInProgress] = useState(false);
  const [isAlreadyAuthenticated, setIsAlreadyAuthenticated] = useState(false);
  const [showFlowchart, setShowFlowchart] = useState(false);
  const [chartZoom, setChartZoom] = useState(1);
  const [chartPan, setChartPan] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [isFullscreen, setIsFullscreen] = useState(false);

  const employeeOptions = useMemo(() => 
    employees.map(e => ({ value: e.name, label: e.name, ticket: e.ticketNumber }))
  , [employees]);

  // Filter employees based on search term
  const filteredOptions = useMemo(() => {
    if (!searchTerm) return [];
    return employeeOptions.filter(opt =>
      opt.label.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [employeeOptions, searchTerm]);

  // Navigation functions
  const zoomIn = () => {
    setChartZoom(prev => Math.min(prev * 1.2, 3));
  };

  const zoomOut = () => {
    setChartZoom(prev => Math.max(prev / 1.2, 0.3));
  };

  const resetView = () => {
    setChartZoom(1);
    setChartPan({ x: 0, y: 0 });
  };

  const handleMouseDown = (e) => {
    setIsDragging(true);
    setDragStart({
      x: e.clientX - chartPan.x,
      y: e.clientY - chartPan.y
    });
  };

  const handleMouseMove = (e) => {
    if (!isDragging) return;
    
    setChartPan({
      x: e.clientX - dragStart.x,
      y: e.clientY - dragStart.y
    });
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const handleWheel = (e) => {
    e.preventDefault();
    const delta = e.deltaY > 0 ? 0.9 : 1.1;
    setChartZoom(prev => Math.max(0.3, Math.min(3, prev * delta)));
  };

  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
  };

  // Reset chart state when closing
  const closeFlowchart = () => {
    setShowFlowchart(false);
    setIsFullscreen(false);
    resetView();
  };

  // Mermaid flowchart definition
  const mermaidChart = `
flowchart TD
    Start(["New Candidate"]) --> CandType{"Candidate Type"}
    CandType -- "Kuehne-Nagel External" --> KN_EXT["Kuehne-Nagel White Collar Template"]
    CandType -- Temp_to_Perm --> KN_TEMP["Kuehne-Nagel Temp to Perm Template"]
    CandType -- Quick Employee --> QUICK["Quick White Collar Template"]
    KN_EXT --> Talmundo["Send Talmundo Buddy Request<br>to HM"]
    KN_TEMP --> Talmundo
    QUICK --> Talmundo
    Talmundo --> IT_Flow{"IT Ticket Process"}
    IT_Flow -- KN External --> IT_KN["Send IT Ticket Request<br>Include SSC in CC"]
    IT_Flow -- Temp to Perm --> IT_TEMP["Send IT Ticket Request<br>Include 'Remove External' remark"]
    IT_Flow -- Quick --> IT_QUICK["Send IT Ticket Request<br>Use preferred name"]
    IT_KN --> IT_Wait{"HM Response?"}
    IT_TEMP --> IT_Wait
    IT_QUICK --> IT_Wait
    IT_Wait -- No response 24hrs --> IT_Remind["Send Reminder<br>CC HM's Manager"]
    IT_Wait -- No response 48hrs --> IT_HRBP["Contact HRBP"]
    IT_Wait -- Response received --> Step2["Step 2: Offer Letter"]
    IT_Remind --> IT_Wait
    IT_HRBP --> IT_Wait
    Step2 --> CB_Offer["Send Offer Letter Notification<br>Step 2 of 7"]
    CB_Offer --> Step3["Step_3:_Clickboarding"]
    Step3 --> CB_Welcome["Send Welcome Email<br>Step 3 of 7"]
    CB_Welcome --> CB_Check{"CB Completed?"}
    CB_Check -- No --> CB_Remind["Send Clickboarding Reminder"]
    CB_Check -- Yes --> Step4["Step_4:_First_Advantage"]
    CB_Remind --> CB_Check
    Step4 --> FADV_Type{"First Contact?"}
    FADV_Type -- Yes --> FADV_First["Send FADV Invitation<br>First Contact - Step 4"]
    FADV_Type -- No --> FADV_Resend["Resend FADV Invitation<br>Step 4"]
    FADV_First --> Step5["Step 5: Screening"]
    FADV_Resend --> Step5
    Step5 --> Screen_Type{"First Contact?"}
    Screen_Type -- "Yes - CB Pending" --> Screen_First_Pend["Send Screening Notification<br>First Contact - Step 5<br>Include CB reminder"]
    Screen_Type -- "Yes - CB Complete" --> Screen_First_Comp["Send Screening Notification<br>First Contact - Step 5"]
    Screen_Type -- No --> Screen_Regular["Send Screening Notification<br>Step 5"]
    Screen_First_Pend --> Step6["Step 6: Results"]
    Screen_First_Comp --> Step6
    Screen_Regular --> Step6
    Step6 --> Test_Status{"Test Status"}
    Test_Status -- Not Taken --> Screen_Wait["Send Welcome - Step 6<br>Waiting for results"]
    Test_Status -- Negative/Dilute --> Retest["Send Retest Required"]
    Test_Status -- Background Ineligible --> BG_Fail{"Send to HM and Candidate"}
    Test_Status -- Drug Positive/Fail --> Drug_Fail{"Send to HM and Candidate"}
    Test_Status -- Refusal to Test --> Refusal["Notify HM - Remove Candidate"]
    Test_Status -- All Pass --> Step8["Step 8: Ready to Hire"]
    Screen_Wait --> Test_Status
    Retest --> Test_Status
    BG_Fail --> BG_HM["Background Ineligible - HM"] & BG_Cand["Background Ineligible - Candidate"]
    Drug_Fail --> Drug_HM["Drug Positive - HM"] & Drug_Cand["Drug Positive - Candidate"]
    BG_HM --> Process_End["End Process"]
    BG_Cand --> Process_End
    Drug_HM --> Process_End
    Drug_Cand --> Process_End
    Refusal --> Process_End
    Step8 --> Hire_Type{"Employee Type"}
    Hire_Type -- Regular --> Ready_Hire["Send Ready to Hire<br>Request start date &amp; cost center"]
    Hire_Type -- White_Collar --> Ready_WC["Send Ready to Hire WC<br>Confirm start date from offer"]
    Ready_Hire --> Welcome_Final["Send Welcome Email<br>Official start date"]
    Ready_WC --> Welcome_Final
    Welcome_Final --> Complete(["Process_Complete"])
    Step3 -.-> Updates{"Update Emails"}
    Step4 -.-> Updates
    Step5 -.-> Updates
    Step6 -.-> Updates
    Updates -- To_HM --> Update_HM["Send HM Update<br>Candidate status table"]
    Updates -- To HM Backup --> Update_HM_Backup["Send HM Update<br>In onboarder's absence"]
    Updates -- To Candidate Backup --> Update_Cand_Backup["Send Candidate Update<br>In onboarder's absence"]

    IT_TEMP
    IT_Remind
    Update_HM_Backup
    Update_Cand_Backup
    
    %% Completed steps (light green) - main happy path only
    Start:::completedBox
    CandType:::completedDecision
    KN_EXT:::completedBox
    Talmundo:::completedBox
    IT_Flow:::completedDecision
    IT_KN:::completedBox
    IT_Wait:::completedDecision
    Step2:::completedStep
    CB_Offer:::completedBox
    Step3:::completedStep
    CB_Welcome:::completedBox
    CB_Check:::completedDecision
    Step4:::completedStep
    FADV_Type:::completedDecision
    FADV_First:::completedBox
    Step5:::completedStep
    Screen_Type:::completedDecision
    Screen_First_Comp:::completedBox
    Step6:::completedStep
    
    %% Remaining steps (original colors)
    KN_TEMP:::processBox
    QUICK:::processBox
    IT_TEMP:::processBox
    IT_QUICK:::processBox
    IT_Remind:::processBox
    IT_HRBP:::processBox
    CB_Remind:::processBox
    FADV_Resend:::processBox
    Screen_First_Pend:::processBox
    Screen_Regular:::processBox
    Test_Status:::decisionBox
    Screen_Wait:::processBox
    Retest:::processBox
    BG_Fail:::failBox
    Drug_Fail:::failBox
    Refusal:::failBox
    Step8:::stepBox
    Process_End:::failBox
    Hire_Type:::decisionBox
    Ready_Hire:::processBox
    Ready_WC:::processBox
    Welcome_Final:::processBox
    Complete:::successBox
    Updates:::decisionBox
    Update_HM:::processBox
    Update_HM_Backup:::processBox
    Update_Cand_Backup:::processBox
    BG_HM:::failBox
    BG_Cand:::failBox
    Drug_HM:::failBox
    Drug_Cand:::failBox
    
    %% Style definitions
    classDef stepBox fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef processBox fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef decisionBox fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef failBox fill:#ffebee,stroke:#c62828,stroke-width:2px
    classDef successBox fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px
    
    %% Completed step styles (light green variants)
    classDef completedBox fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px
    classDef completedStep fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px
    classDef completedDecision fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px

    %% Click events
    click Start "handleMermaidClick" "New Candidate"
    click CandType "handleMermaidClick" "Candidate Type"
    click KN_EXT "handleMermaidClick" "Kuehne-Nagel White Collar Template"
    click KN_TEMP "handleMermaidClick" "Kuehne-Nagel Temp to Perm Template"
    click QUICK "handleMermaidClick" "Quick White Collar Template"
    click Talmundo "handleMermaidClick" "Send Talmundo Buddy Request to HM"
    click IT_Flow "handleMermaidClick" "IT Ticket Process"
    click IT_KN "handleMermaidClick" "Send IT Ticket Request - Include SSC in CC"
    click IT_TEMP "handleMermaidClick" "Send IT Ticket Request - Include Remove External remark"
    click IT_QUICK "handleMermaidClick" "Send IT Ticket Request - Use preferred name"
    click IT_Wait "handleMermaidClick" "HM Response?"
    click IT_Remind "handleMermaidClick" "Send Reminder - CC HM's Manager"
    click IT_HRBP "handleMermaidClick" "Contact HRBP"
    click Step2 "handleMermaidClick" "Step 2: Offer Letter"
    click CB_Offer "handleMermaidClick" "Send Offer Letter Notification - Step 2 of 7"
    click Step3 "handleMermaidClick" "Step 3: Clickboarding"
    click CB_Welcome "handleMermaidClick" "Send Welcome Email - Step 3 of 7"
    click CB_Check "handleMermaidClick" "CB Completed?"
    click CB_Remind "handleMermaidClick" "Send Clickboarding Reminder"
    click Step4 "handleMermaidClick" "Step 4: First Advantage"
    click FADV_Type "handleMermaidClick" "First Contact?"
    click FADV_First "handleMermaidClick" "Send FADV Invitation - First Contact - Step 4"
    click FADV_Resend "handleMermaidClick" "Resend FADV Invitation - Step 4"
    click Step5 "handleMermaidClick" "Step 5: Screening"
    click Screen_Type "handleMermaidClick" "First Contact?"
    click Screen_First_Pend "handleMermaidClick" "Send Screening Notification - First Contact - Step 5 - Include CB reminder"
    click Screen_First_Comp "handleMermaidClick" "Send Screening Notification - First Contact - Step 5"
    click Screen_Regular "handleMermaidClick" "Send Screening Notification - Step 5"
    click Step6 "handleMermaidClick" "Step 6: Results"
    click Test_Status "handleMermaidClick" "Test Status"
    click Screen_Wait "handleMermaidClick" "Send Welcome - Step 6 - Waiting for results"
    click Retest "handleMermaidClick" "Send Retest Required"
    click BG_Fail "handleMermaidClick" "Send to HM and Candidate"
    click Drug_Fail "handleMermaidClick" "Send to HM and Candidate"
    click Refusal "handleMermaidClick" "Notify HM - Remove Candidate"
    click Step8 "handleMermaidClick" "Step 8: Ready to Hire"
    click Process_End "handleMermaidClick" "End Process"
    click Hire_Type "handleMermaidClick" "Employee Type"
    click Ready_Hire "handleMermaidClick" "Send Ready to Hire - Request start date & cost center"
    click Ready_WC "handleMermaidClick" "Send Ready to Hire WC - Confirm start date from offer"
    click Welcome_Final "handleMermaidClick" "Send Welcome Email - Official start date"
    click Complete "handleMermaidClick" "Process Complete"
    click Updates "handleMermaidClick" "Update Emails"
    click Update_HM "handleMermaidClick" "Send HM Update - Candidate status table"
    click Update_HM_Backup "handleMermaidClick" "Send HM Update - In onboarder's absence"
    click Update_Cand_Backup "handleMermaidClick" "Send Candidate Update - In onboarder's absence"
    click BG_HM "handleMermaidClick" "Background Ineligible - HM"
    click BG_Cand "handleMermaidClick" "Background Ineligible - Candidate"
    click Drug_HM "handleMermaidClick" "Drug Positive - HM"
    click Drug_Cand "handleMermaidClick" "Drug Positive - Candidate"
`;

  // Handle Mermaid diagram clicks
  const handleMermaidClick = (stepTitle) => {
    const employeeName = selectedEmployee ? selectedEmployee.label : 'Selected Employee';
    alert(`Send email: "${stepTitle}" for ${employeeName}`);
  };

  // Load Mermaid script dynamically
  React.useEffect(() => {
    if (showFlowchart && !window.mermaid) {
      const script = document.createElement('script');
      script.src = 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js';
      script.onload = () => {
        window.mermaid.initialize({ 
          startOnLoad: true,
          theme: 'default',
          flowchart: {
            useMaxWidth: true,
            htmlLabels: true,
            curve: 'basis'
          },
          securityLevel: 'loose'
        });
        
        // Make the click handler globally available
        window.handleMermaidClick = handleMermaidClick;
        
        window.mermaid.contentLoaded();
      };
      document.head.appendChild(script);
    } else if (showFlowchart && window.mermaid) {
      // Make the click handler globally available
      window.handleMermaidClick = handleMermaidClick;
      
      // Re-render if mermaid is already loaded
      setTimeout(() => {
        window.mermaid.contentLoaded();
      }, 100);
    }
  }, [showFlowchart, selectedEmployee]);

  // Handle global mouse events for dragging
  React.useEffect(() => {
    const handleGlobalMouseMove = (e) => {
      if (isDragging) {
        handleMouseMove(e);
      }
    };

    const handleGlobalMouseUp = () => {
      if (isDragging) {
        handleMouseUp();
      }
    };

    if (isDragging) {
      document.addEventListener('mousemove', handleGlobalMouseMove);
      document.addEventListener('mouseup', handleGlobalMouseUp);
    }

    return () => {
      document.removeEventListener('mousemove', handleGlobalMouseMove);
      document.removeEventListener('mouseup', handleGlobalMouseUp);
    };
  }, [isDragging, dragStart.x, dragStart.y]);

  // Handle fullscreen escape key
  React.useEffect(() => {
    const handleEscapeKey = (e) => {
      if (e.key === 'Escape' && isFullscreen) {
        setIsFullscreen(false);
      }
    };

    if (isFullscreen) {
      document.addEventListener('keydown', handleEscapeKey);
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'auto';
    }

    return () => {
      document.removeEventListener('keydown', handleEscapeKey);
      document.body.style.overflow = 'auto';
    };
  }, [isFullscreen]);

  // Check if email service is running
  const checkEmailService = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5002/api/health');
      if (response.ok) {
        setEmailServiceStatus('online');
        return true;
      } else {
        setEmailServiceStatus('offline');
        return false;
      }
    } catch (error) {
      setEmailServiceStatus('offline');
      return false;
    }
  };

  // Check authentication status
  const checkAuthStatus = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5002/api/auth/status');
      if (response.ok) {
        const data = await response.json();
        return data.authenticated;
      }
    } catch (error) {
      console.log('Auth status check failed:', error);
    }
    return false;
  };

  // Check for device code in email service logs
  const checkForDeviceCode = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5002/api/auth/device-code');
      if (response.ok) {
        const data = await response.json();
        if (data.deviceCode) {
          setDeviceCode(data.deviceCode);
          return true;
        }
      }
    } catch (error) {
      console.log('Device code endpoint not available');
    }
    return false;
  };

  // Poll for device code during authentication
  const pollForDeviceCode = async () => {
    let attempts = 0;
    const maxAttempts = 30; // Poll for up to 30 seconds
    
    const poll = async () => {
      if (attempts >= maxAttempts) {
        return;
      }
      
      const hasCode = await checkForDeviceCode();
      if (!hasCode && attempts < maxAttempts) {
        attempts++;
        setTimeout(poll, 1000); // Poll every second
      }
    };
    
    await poll();
  };

  // Fetch emails for selected employee
  const fetchEmployeeEmails = async (employeeName) => {
    setIsLoadingEmails(true);
    setEmailError('');
    setAuthInProgress(false);
    setDeviceCode('');
    
    try {
      // First check if email service is running
      const serviceOnline = await checkEmailService();
      if (!serviceOnline) {
        setEmailError('Email service is not running. Please start the email service first.');
        setIsLoadingEmails(false);
        return;
      }

      // Check if already authenticated
      const isAuthenticated = await checkAuthStatus();
      
      if (!isAuthenticated) {
        // Show authentication modal before making the request
        setShowAuthModal(true);
        setAuthInProgress(true);
        setIsAlreadyAuthenticated(false);

        // Start polling for device code
        pollForDeviceCode();
      } else {
        // User is already authenticated, show brief confirmation
        setShowAuthModal(true);
        setIsAlreadyAuthenticated(true);
        setAuthInProgress(false);
        
        // Hide the modal after a short delay
        setTimeout(() => {
          setShowAuthModal(false);
          setIsAlreadyAuthenticated(false);
        }, 1500);
      }

      const response = await fetch('http://127.0.0.1:5002/api/emails/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          employeeName: employeeName,
          count: 25
        })
      });

      // Close auth modal if it was shown
      if (!isAlreadyAuthenticated) {
        setShowAuthModal(false);
        setAuthInProgress(false);
      }

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to fetch emails');
      }

      const data = await response.json();
      setEmailData(data);
    } catch (error) {
      console.error('Error fetching emails:', error);
      setEmailError(`Failed to fetch emails: ${error.message}`);
      setShowAuthModal(false);
      setAuthInProgress(false);
      setIsAlreadyAuthenticated(false);
    } finally {
      setIsLoadingEmails(false);
    }
  };

  // Get progress data for selected employee
  const handleCheckProgress = async () => {
    if (!selectedEmployee) return;

    const employeeRecords = excelData.rows.filter(row => {
      const employeeName = row[5];
      return employeeName && employeeName.toString().trim().toLowerCase() === selectedEmployee.value.toLowerCase();
    });

    const progressInfo = {
      employeeName: selectedEmployee.label,
      totalRecords: employeeRecords.length,
      records: employeeRecords.map((row, i) => ({
        ticketNumber: row[0],
        fullRow: row,
        rowIndex: excelData.rows.findIndex(r => r.join('') === row.join('')) + 1 
      })),
      columns: excelData.headers
    };

    setProgressData(progressInfo);
    
    // Also fetch emails for this employee
    await fetchEmployeeEmails(selectedEmployee.label);
  };

  const handleEmployeeSelect = (employee) => {
    setSelectedEmployee(employee);
    setSearchTerm(employee.label);
  };
  
  const reset = () => {
    setSearchTerm('');
    setSelectedEmployee(null);
    setProgressData(null);
    setEmailData(null);
    setEmailError('');
    setShowAuthModal(false);
    setDeviceCode('');
    setAuthInProgress(false);
    setIsAlreadyAuthenticated(false);
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Unknown';
    try {
      const date = new Date(dateString);
      return date.toLocaleString();
    } catch {
      return 'Invalid Date';
    }
  };

  const getColumnLetter = (index) => String.fromCharCode(65 + index);

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text).then(() => {
      // Could add a toast notification here
      console.log('Copied to clipboard:', text);
    });
  };

  return (
    <>
      {/* Authentication Modal */}
      {showAuthModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.7)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000
        }}>
          <div style={{
            backgroundColor: 'white',
            borderRadius: '12px',
            padding: '32px',
            maxWidth: '500px',
            width: '90%',
            boxShadow: '0 20px 40px rgba(0, 0, 0, 0.3)',
            textAlign: 'center'
          }}>
            <Shield size={48} style={{color: 'var(--kn-blue)', marginBottom: '16px'}} />
            <h2 style={{ color: 'var(--kn-blue)', marginBottom: '16px' }}>
              Microsoft Authentication Required
            </h2>
            
            {isAlreadyAuthenticated ? (
              <>
                <CheckCircle size={48} style={{color: '#28a745', marginBottom: '16px'}} />
                <h2 style={{ color: '#28a745', marginBottom: '16px' }}>
                  Already Authenticated!
                </h2>
                <p style={{ marginBottom: '24px', fontSize: '16px', color: '#28a745' }}>
                  You're already signed in. Fetching your emails now...
                </p>
                <div style={{ 
                  display: 'inline-block',
                  width: '32px',
                  height: '32px',
                  border: '3px solid #f3f3f3',
                  borderTop: '3px solid #28a745',
                  borderRadius: '50%',
                  animation: 'spin 1s linear infinite'
                }}>
                </div>
              </>
            ) : authInProgress ? (
              <>
                <p style={{ marginBottom: '24px', fontSize: '16px' }}>
                  Please complete authentication to access your emails.
                </p>
                
                {deviceCode ? (
                  <>
                    <div style={{ 
                      marginBottom: '24px', 
                      padding: '24px', 
                      backgroundColor: '#e8f5e8', 
                      borderRadius: '12px',
                      border: '2px solid #4caf50'
                    }}>
                      <div style={{display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px'}}>
                        <Shield size={18} style={{color: '#2e7d32'}} />
                        <h3 style={{ color: '#2e7d32', margin: 0, fontSize: '18px' }}>
                          Your Device Code:
                        </h3>
                      </div>
                      <div style={{
                        fontSize: '32px',
                        fontFamily: 'monospace',
                        fontWeight: 'bold',
                        color: '#1565c0',
                        backgroundColor: 'white',
                        padding: '16px',
                        borderRadius: '8px',
                        border: '2px solid #1976d2',
                        letterSpacing: '4px',
                        marginBottom: '12px'
                      }}>
                        {deviceCode}
                      </div>
                      <button 
                        onClick={() => copyToClipboard(deviceCode)}
                        style={{
                          padding: '8px 16px',
                          fontSize: '14px',
                          border: 'none',
                          borderRadius: '6px',
                          backgroundColor: '#1976d2',
                          color: 'white',
                          cursor: 'pointer',
                          fontWeight: '500',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '6px'
                        }}
                      >
                        <Copy size={14} />
                        Copy Code
                      </button>
                    </div>
                    
                    <div style={{ marginBottom: '24px', padding: '20px', backgroundColor: '#f8f9fa', borderRadius: '8px' }}>
                      <h3 style={{ color: '#333', marginBottom: '16px' }}>Quick Steps:</h3>
                      <ol style={{ textAlign: 'left', paddingLeft: '20px', lineHeight: '1.8', fontSize: '15px' }}>
                        <li style={{ marginBottom: '8px' }}>
                          <strong>Click the button below</strong> to open the authentication page
                        </li>
                        <li style={{ marginBottom: '8px' }}>
                          <strong>Enter this code:</strong> <code style={{ 
                            backgroundColor: '#e3f2fd', 
                            padding: '2px 6px', 
                            borderRadius: '4px',
                            fontWeight: 'bold',
                            color: '#1565c0'
                          }}>{deviceCode}</code>
                        </li>
                        <li style={{ marginBottom: '8px' }}>
                          <strong>Sign in</strong> with your Microsoft account
                        </li>
                        <li>
                          <strong>Grant permissions</strong> and return to this app
                        </li>
                      </ol>
                    </div>
                  </>
                ) : (
                  <>
                    <div style={{ marginBottom: '24px', padding: '20px', backgroundColor: '#fff3cd', borderRadius: '8px' }}>
                      <div style={{display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px'}}>
                        <Clock size={18} style={{color: '#856404'}} />
                        <h3 style={{ color: '#856404', margin: 0 }}>Generating Device Code...</h3>
                      </div>
                      <p style={{ margin: 0, color: '#856404' }}>
                        Please wait while we generate your authentication code. This usually takes a few seconds.
                      </p>
                    </div>
                    
                    <div style={{ marginBottom: '24px', padding: '20px', backgroundColor: '#f8f9fa', borderRadius: '8px' }}>
                      <h3 style={{ color: '#333', marginBottom: '16px' }}>What happens next:</h3>
                      <ol style={{ textAlign: 'left', paddingLeft: '20px', lineHeight: '1.6' }}>
                        <li style={{ marginBottom: '8px' }}>
                          A unique device code will appear above
                        </li>
                        <li style={{ marginBottom: '8px' }}>
                          You'll be able to copy the code easily
                        </li>
                        <li style={{ marginBottom: '8px' }}>
                          Click the button to open the Microsoft login page
                        </li>
                        <li>
                          Enter the code and sign in with your Microsoft account
                        </li>
                      </ol>
                    </div>
                  </>
                )}

                <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
                  <button
                    onClick={() => setShowAuthModal(false)}
                    style={{
                      padding: '10px 20px',
                      border: '1px solid #ccc',
                      borderRadius: '6px',
                      backgroundColor: '#f8f9fa',
                      cursor: 'pointer'
                    }}
                  >
                    Cancel
                  </button>
                  <button
                    onClick={() => window.open('https://microsoft.com/devicelogin', '_blank')}
                    style={{
                      padding: '10px 20px',
                      border: 'none',
                      borderRadius: '6px',
                      backgroundColor: 'var(--kn-blue)',
                      color: 'white',
                      cursor: 'pointer',
                      fontWeight: '500',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px'
                    }}
                  >
                    <ExternalLink size={16} />
                    Open Authentication Page
                  </button>
                </div>
              </>
            ) : (
              <>
                <p style={{ marginBottom: '24px' }}>
                  Preparing to authenticate with Microsoft Graph...
                </p>
                <div style={{ 
                  display: 'inline-block',
                  width: '32px',
                  height: '32px',
                  border: '3px solid #f3f3f3',
                  borderTop: '3px solid var(--kn-blue)',
                  borderRadius: '50%',
                  animation: 'spin 1s linear infinite'
                }}>
                </div>
              </>
            )}
          </div>
        </div>
      )}

      <div className="page-header" style={{textAlign: 'left', marginBottom: '16px'}}>
        <h1 className="page-title" style={{fontSize: '2rem'}}>
          Employee Progress
        </h1>
        <p className="page-subtitle" style={{fontSize: '1rem', color: 'var(--kn-text-secondary)'}}>
          Select an employee to view their assigned records and emails with their name in the subject line.
        </p>
      </div>
      
      <div className="employee-selector">
        <div className="card">
          <div style={{display: 'flex', alignItems: 'center', gap: '16px', flexWrap: 'wrap'}}>
            {/* Search/Filter Input */}
            <div className="search-container" style={{flexGrow: 1, minWidth: '300px', marginBottom: 0}}>
              <User size={16} style={{position: 'absolute', left: '12px', top: '12px', color: 'var(--kn-text-secondary)'}} />
              <input
                type="text"
                placeholder="Search for an employee..."
                value={searchTerm}
                onChange={(e) => {
                  setSearchTerm(e.target.value);
                  setSelectedEmployee(null);
                  setProgressData(null);
                  setEmailData(null);
                  setEmailError('');
                }}
                className="employee-dropdown"
                style={{paddingLeft: '40px'}}
              />
               {searchTerm && filteredOptions.length > 0 && !selectedEmployee && (
                <div style={{
                  position: 'absolute', top: '100%', left: 0, right: 0,
                  maxHeight: '250px', overflowY: 'auto',
                  border: '1px solid var(--kn-border-color)', borderRadius: '8px',
                  marginTop: '4px', backgroundColor: 'var(--kn-white)',
                  zIndex: 100, boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
                }}>
                  {filteredOptions.map((opt, index) => (
                    <div
                      key={index}
                      onClick={() => handleEmployeeSelect(opt)}
                      style={{ padding: '12px 16px', cursor: 'pointer', borderBottom: index < filteredOptions.length - 1 ? '1px solid var(--kn-border-color)' : 'none' }}
                      onMouseEnter={(e) => e.target.style.backgroundColor = 'var(--kn-light-blue)'}
                      onMouseLeave={(e) => e.target.style.backgroundColor = 'var(--kn-white)'}
                    >
                      {opt.label}
                    </div>
                  ))}
                </div>
              )}
            </div>
            
            <div style={{display: 'flex', gap: '10px'}}>
              <button
                className="btn"
                onClick={handleCheckProgress}
                disabled={!selectedEmployee || isLoadingEmails}
                style={{ opacity: (selectedEmployee && !isLoadingEmails) ? 1 : 0.6 }}
              >
                {isLoadingEmails ? 'Loading...' : 'Check Progress'}
              </button>
              <button className="btn btn-secondary" onClick={reset}>
                Reset
              </button>
              <button 
                className="btn btn-secondary" 
                onClick={() => setShowFlowchart(!showFlowchart)}
                style={{ 
                  backgroundColor: showFlowchart ? 'var(--kn-blue)' : '',
                  color: showFlowchart ? 'white' : '',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px'
                }}
              >
                <BarChart3 size={16} />
                {showFlowchart ? 'Hide Process Flow' : 'Show Process Flow'}
              </button>
            </div>
          </div>
        </div>

        {/* Email Service Status */}
        {emailServiceStatus !== 'unknown' && (
          <div className="card" style={{marginTop: '16px'}}>
            <div style={{display: 'flex', alignItems: 'center', gap: '12px'}}>
              {emailServiceStatus === 'online' ? (
                <CheckCircle size={16} style={{color: '#22c55e'}} />
              ) : (
                <XCircle size={16} style={{color: '#ef4444'}} />
              )}
              <span style={{fontWeight: '500'}}>
                Email Service: {emailServiceStatus === 'online' ? 'Online' : 'Offline'}
              </span>
              {emailServiceStatus === 'offline' && (
                <span style={{color: 'var(--kn-text-secondary)', fontSize: '14px'}}>
                  Start the email service to view emails
                </span>
              )}
            </div>
          </div>
        )}

        {/* Email Error */}
        {emailError && (
          <div className="card" style={{marginTop: '16px', borderLeft: '4px solid #ef4444'}}>
            <div style={{display: 'flex', alignItems: 'flex-start', gap: '12px'}}>
              <AlertCircle size={20} style={{color: '#ef4444', marginTop: '2px'}} />
              <div>
                <h4 style={{color: '#ef4444', marginBottom: '8px', margin: '0 0 8px 0'}}>Email Service Error</h4>
                <p style={{color: 'var(--kn-text-secondary)', margin: 0}}>{emailError}</p>
              </div>
            </div>
          </div>
        )}

        {/* Progress Results */}
        {progressData && (
          <div className="card">
            <h3 style={{marginBottom: '16px', color: 'var(--kn-blue)'}}>
              Progress Report for: {progressData.employeeName}
            </h3>

            <div className="stats-grid">
              <div className="stat-card">
                <div className="stat-label">Total Records</div>
                <div className="stat-number">{progressData.totalRecords}</div>
              </div>
              <div className="stat-card">
                <div className="stat-label">Unique Tickets</div>
                <div className="stat-number">{new Set(progressData.records.map(r => r.ticketNumber)).size}</div>
              </div>
              {emailData && (
                <>
                  <div className="stat-card">
                    <div className="stat-label">Related Emails</div>
                    <div className="stat-number">{emailData.emails.length}</div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-label">Unread Emails</div>
                    <div className="stat-number">{emailData.emails.filter(e => !e.isRead).length}</div>
                  </div>
                </>
              )}
            </div>

            {progressData.totalRecords > 0 ? (
              <div className="table-container">
                <div className="scrollable-table" style={{ maxHeight: '400px' }}>
                  <table className="data-table">
                    <thead>
                      {/* First header row - merged headers like "General Information" */}
                      {excelData.mergedHeaders && (
                        <tr>
                          {excelData.mergedHeaders.map((header, index) => {
                            // Check if this is the start of a merged section
                            const isFirstInMerge = header && header.trim();
                            const nextHeaders = excelData.mergedHeaders.slice(index + 1);
                            const mergeLength = isFirstInMerge ? 
                              1 + nextHeaders.findIndex(h => h && h.trim() && h !== header) : 1;
                            const actualMergeLength = mergeLength === 0 ? 
                              nextHeaders.length + 1 : mergeLength;
                            
                            // Skip cells that are part of a previous merge
                            const isPreviousMerge = index > 0 && 
                              excelData.mergedHeaders.slice(0, index).some((prevHeader, prevIndex) => {
                                if (!prevHeader || !prevHeader.trim()) return false;
                                const prevMergeEnd = excelData.mergedHeaders.slice(prevIndex + 1)
                                  .findIndex(h => h && h.trim() && h !== prevHeader);
                                const prevActualEnd = prevMergeEnd === -1 ? 
                                  excelData.mergedHeaders.length - 1 : prevIndex + prevMergeEnd;
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
                        {progressData.columns.map((header, index) => (
                          <th 
                            key={index}
                            style={{
                              backgroundColor: 'var(--kn-light-blue)',
                              borderBottom: '2px solid var(--kn-border-color)'
                            }}
                          >
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
                              <strong>{getColumnLetter(index)}</strong>
                            )}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {progressData.records.map((record, index) => (
                        <tr key={index}>
                          {record.fullRow.map((cell, cellIndex) => (
                            <td key={cellIndex}>
                              {cell || ''}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            ) : (
              <div style={{ textAlign: 'center', padding: '30px', color: 'var(--kn-text-secondary)' }}>
                <h4>No records found for this employee.</h4>
              </div>
            )}
          </div>
        )}

        {/* Email Results */}
        {emailData && (
          <div className="card">
            <h3 style={{marginBottom: '16px', color: 'var(--kn-blue)'}}>
              Emails with "{emailData.employeeName}" in Subject Line
            </h3>
            
            {emailData.emails.length > 0 ? (
              <div style={{display: 'flex', flexDirection: 'column', gap: '12px'}}>
                {emailData.emails.map((email, index) => (
                  <div 
                    key={index} 
                    style={{
                      border: '1px solid var(--kn-border-color)',
                      borderRadius: '8px',
                      padding: '16px',
                      backgroundColor: email.isRead ? 'var(--kn-white)' : 'var(--kn-light-blue)',
                      borderLeft: email.isRead ? '4px solid var(--kn-gray)' : '4px solid var(--kn-blue)'
                    }}
                  >
                    <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px'}}>
                      <div style={{flexGrow: 1}}>
                        <div style={{fontWeight: '600', marginBottom: '4px', color: 'var(--kn-blue)'}}>
                          {email.subject || 'No Subject'}
                        </div>
                        <div style={{fontSize: '14px', color: 'var(--kn-text-secondary)', marginBottom: '4px'}}>
                          From: {email.from.name} ({email.from.address})
                        </div>
                        <div style={{fontSize: '12px', color: 'var(--kn-text-secondary)'}}>
                          {formatDate(email.receivedDateTime)}
                        </div>
                      </div>
                      <div style={{display: 'flex', gap: '8px', alignItems: 'center'}}>
                        {email.hasAttachments && (
                          <Paperclip size={16} style={{color: 'var(--kn-text-secondary)'}} title="Has attachments" />
                        )}
                        <span style={{
                          fontSize: '12px',
                          padding: '2px 8px',
                          borderRadius: '12px',
                          backgroundColor: email.isRead ? 'var(--kn-gray)' : 'var(--kn-blue)',
                          color: email.isRead ? 'var(--kn-text-secondary)' : 'white',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '4px'
                        }}>
                          {email.isRead ? <Mail size={10} /> : <Activity size={10} />}
                          {email.isRead ? 'Read' : 'Unread'}
                        </span>
                      </div>
                    </div>
                    {email.bodyPreview && (
                      <div style={{
                        fontSize: '14px',
                        color: 'var(--kn-text-secondary)',
                        fontStyle: 'italic',
                        marginTop: '8px',
                        padding: '8px',
                        backgroundColor: 'rgba(0,0,0,0.05)',
                        borderRadius: '4px'
                      }}>
                        {email.bodyPreview}
                      </div>
                    )}
                  </div>
                ))}
                
                {emailData.hasMore && (
                  <div style={{textAlign: 'center', padding: '16px', color: 'var(--kn-text-secondary)'}}>
                    <em>More emails available...</em>
                  </div>
                )}
              </div>
            ) : (
              <div style={{ textAlign: 'center', padding: '30px', color: 'var(--kn-text-secondary)' }}>
                <h4>No emails found with "{emailData.employeeName}" in the subject line.</h4>
                <p>Try checking if there are emails with this employee's name in the subject.</p>
              </div>
            )}
          </div>
        )}

        {/* Process Flow Visualization */}
        {showFlowchart && (
          <div 
            className="card" 
            style={{
              marginTop: '16px',
              position: isFullscreen ? 'fixed' : 'relative',
              top: isFullscreen ? 0 : 'auto',
              left: isFullscreen ? 0 : 'auto',
              right: isFullscreen ? 0 : 'auto',
              bottom: isFullscreen ? 0 : 'auto',
              zIndex: isFullscreen ? 9999 : 'auto',
              width: isFullscreen ? '100vw' : 'auto',
              height: isFullscreen ? '100vh' : 'auto',
              maxHeight: isFullscreen ? '100vh' : '80vh',
              backgroundColor: 'white'
            }}
          >
            <div style={{display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px', padding: isFullscreen ? '16px' : '0'}}>
              <div style={{display: 'flex', alignItems: 'center', gap: '8px'}}>
                <BarChart3 size={20} style={{color: 'var(--kn-blue)'}} />
                <h3 style={{color: 'var(--kn-blue)', margin: 0}}>
                  Employee Onboarding Process Flow
                </h3>
              </div>
              <div style={{display: 'flex', gap: '8px', alignItems: 'center', flexWrap: 'wrap'}}>
                <div style={{display: 'flex', gap: '4px', alignItems: 'center', backgroundColor: '#f0f0f0', borderRadius: '6px', padding: '2px'}}>
                  <button 
                    className="btn btn-secondary"
                    onClick={zoomOut}
                    disabled={chartZoom <= 0.3}
                    style={{fontSize: '14px', padding: '6px 10px', minWidth: 'auto', display: 'flex', alignItems: 'center'}}
                    title="Zoom Out"
                  >
                    <ZoomOut size={14} />
                  </button>
                  <span style={{fontSize: '12px', minWidth: '45px', textAlign: 'center', color: '#666'}}>
                    {Math.round(chartZoom * 100)}%
                  </span>
                  <button 
                    className="btn btn-secondary"
                    onClick={zoomIn}
                    disabled={chartZoom >= 3}
                    style={{fontSize: '14px', padding: '6px 10px', minWidth: 'auto', display: 'flex', alignItems: 'center'}}
                    title="Zoom In"
                  >
                    <ZoomIn size={14} />
                  </button>
                </div>
                <button 
                  className="btn btn-secondary"
                  onClick={resetView}
                  style={{fontSize: '12px', padding: '6px 12px', display: 'flex', alignItems: 'center', gap: '4px'}}
                  title="Reset View"
                >
                  <RotateCcw size={14} />
                  Reset
                </button>
                <button 
                  className="btn btn-secondary"
                  onClick={toggleFullscreen}
                  style={{fontSize: '12px', padding: '6px 12px', display: 'flex', alignItems: 'center', gap: '4px'}}
                  title={isFullscreen ? "Exit Fullscreen" : "Fullscreen"}
                >
                  {isFullscreen ? <Minimize2 size={14} /> : <Maximize2 size={14} />}
                  {isFullscreen ? 'Exit' : 'Full'}
                </button>
                <button 
                  className="btn btn-secondary"
                  onClick={closeFlowchart}
                  style={{fontSize: '12px', padding: '6px 12px', display: 'flex', alignItems: 'center'}}
                  title="Close"
                >
                  <X size={14} />
                </button>
              </div>
            </div>
            
            <div style={{
              border: '1px solid var(--kn-border-color)',
              borderRadius: '8px',
              backgroundColor: '#fafafa',
              overflow: 'hidden',
              height: isFullscreen ? 'calc(100vh - 120px)' : '60vh',
              position: 'relative',
              cursor: isDragging ? 'grabbing' : 'grab'
            }}>
              <div 
                style={{
                  width: '100%',
                  height: '100%',
                  overflow: 'hidden',
                  position: 'relative'
                }}
                onMouseDown={handleMouseDown}
                onMouseMove={handleMouseMove}
                onMouseUp={handleMouseUp}
                onMouseLeave={handleMouseUp}
                onWheel={handleWheel}
              >
                <div 
                  id="mermaid-chart"
                  className="mermaid"
                  style={{
                    transform: `translate(${chartPan.x}px, ${chartPan.y}px) scale(${chartZoom})`,
                    transformOrigin: '0 0',
                    transition: isDragging ? 'none' : 'transform 0.1s ease-out',
                    userSelect: 'none',
                    pointerEvents: isDragging ? 'none' : 'auto'
                  }}
                >
                  {mermaidChart}
                </div>
              </div>
              
              {/* Navigation hint */}
              <div style={{
                position: 'absolute',
                bottom: '8px',
                left: '8px',
                backgroundColor: 'rgba(0,0,0,0.7)',
                color: 'white',
                padding: '4px 8px',
                borderRadius: '4px',
                fontSize: '11px',
                pointerEvents: 'none',
                opacity: 0.8,
                display: 'flex',
                alignItems: 'center',
                gap: '4px'
              }}>
                <Lightbulb size={12} />
                Drag to pan • Scroll to zoom • Use controls above
              </div>
            </div>
            
            <div style={{marginTop: '16px', padding: '12px', backgroundColor: 'var(--kn-light-blue)', borderRadius: '6px'}}>
              <h4 style={{margin: '0 0 8px 0', color: 'var(--kn-blue)'}}>Legend:</h4>
              <div style={{display: 'flex', flexWrap: 'wrap', gap: '16px', fontSize: '14px'}}>
                <div style={{display: 'flex', alignItems: 'center', gap: '6px'}}>
                  <div style={{width: '16px', height: '16px', backgroundColor: '#e1f5fe', border: '2px solid #01579b'}}></div>
                  <span>Process Steps</span>
                </div>
                <div style={{display: 'flex', alignItems: 'center', gap: '6px'}}>
                  <div style={{width: '16px', height: '16px', backgroundColor: '#fff3e0', border: '2px solid #e65100'}}></div>
                  <span>Decision Points</span>
                </div>
                <div style={{display: 'flex', alignItems: 'center', gap: '6px'}}>
                  <div style={{width: '16px', height: '16px', backgroundColor: '#f3e5f5', border: '2px solid #4a148c'}}></div>
                  <span>Actions</span>
                </div>
                <div style={{display: 'flex', alignItems: 'center', gap: '6px'}}>
                  <div style={{width: '16px', height: '16px', backgroundColor: '#e8f5e8', border: '2px solid #2e7d32'}}></div>
                  <span>Success/Complete</span>
                </div>
                <div style={{display: 'flex', alignItems: 'center', gap: '6px'}}>
                  <div style={{width: '16px', height: '16px', backgroundColor: '#ffebee', border: '2px solid #c62828'}}></div>
                  <span>Failure/End</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </>
  );
};

export default EmployeeSelector; 