import { useState } from 'react';
import axios from "axios";
import './App.css';
import Spreadsheet from "react-spreadsheet";


function App() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [selectedDate, setSelectedDate] = useState('');
  const [results, setResults] = useState<{ revenue: string[]; cost: string[];    date: string[]} | null>(null);
  const [loading, setLoading] = useState(false); // Loading state

  const [hasError, setHasError] = useState(false);


  const onFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSelectedFile(event.target.files?.[0] || null);
    
  };

  const onDateChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSelectedDate(event.target.value);
  };
let headerRow: any[] = [];
let revenueRow: any[] = [];
let grossProfitRow: any[] = [];


const spreadsheet = () => {
  if (!results) return [];

  if (results) {
headerRow.push({ value: "Years" }); 

for (let i = 0; i < results.date.length; i++) {
  headerRow.push({ value: results.date[i] }); 
}
 
revenueRow.push({ value: "Revenue" });

for (let i = 0; i < results.revenue.length; i++) {
  revenueRow.push({ value: results.revenue[i] });
}
grossProfitRow.push({ value: "Gross Profit" });

for (let i = 0; i < results.revenue.length; i++) {
  const revenueValue = results.revenue[i].replace(/[^0-9.-]+/g, "");
  const costValue = results.cost[i].replace(/[^0-9.-]+/g, "");

  const profit = Number(revenueValue) - Number(costValue);

    grossProfitRow.push({ value: profit.toLocaleString() });
  }
}
    
  return [headerRow, revenueRow, grossProfitRow];
}



  

  const onFileUpload = async () => {
    if (!selectedFile) {
      alert("Please select a file");
      return;
    }

    const formData = new FormData();
    formData.append("file", selectedFile);
    if (selectedDate) {
      formData.append("period_end_date", selectedDate);
    }

    try {
      setLoading(true); // Show loading
      const response = await axios.post(
        "http://127.0.0.1:8000/api/extract/",
        formData
      );

      const data = response.data.results;
      const date = response.data.period_end_date;
      let dateValues = Array.isArray(date) ? date : [date];
   
      const revenueValues = Array.isArray(data.revenue)? data.revenue: (data.revenue ? [data.revenue] : []);

      const costValues = Array.isArray(data.cos)? data.cos: (data.cos ? [data.cos] : []);
      setResults({
  revenue: revenueValues.length ? revenueValues : ["Error: No Revenue Found"],
  cost: costValues.length ? costValues : ["Error: No Cost of Sales found"],
  date: dateValues,
});
setHasError(false);



    } catch (error: any) {

 const status = error.response?.status;
  const message = error.response?.data || error.message;
  setHasError(true);

  if (status === 500) {
    alert("Internal server error. Please check your file and try again.");
  } else {
    alert(`Upload failed: ${message} Status Code: ${status}`);
  }

  
      console.error("Upload error:", error.response?.data || error.message);
      setResults({
        revenue: ["Error: No Revenue Found"],
        cost: ["Error: No Cost of Sales found"],
        date:[]
      });
    } finally {
      setLoading(false); // Hide loading
    }
  };




  return (
    <div>
      <h1 className='block-3d'>Financial Value Extractor </h1>
      <h3 style={{color: '#81e785ff', fontSize:'25px',fontFamily:'monospace', fontStyle:'inherit'}}>Please upload the 10-K document and an optional period date</h3>

      <div>
        <input type="file" onChange={onFileChange} />
        <input type="date" onChange={onDateChange} />
        <button onClick={onFileUpload}>Upload!</button>
      </div>

      {loading && <p>Processing your file, please wait...</p>}

      {!loading && !hasError&&results && <Spreadsheet
  data={spreadsheet()}
  columnLabels={[]}
  rowLabels={[]}
  hideRowIndicators={true}
  hideColumnIndicators={true}
  Cell={(props) => {
    const isFirstColumn = props.column === 0;

    const isGreenText = isFirstColumn ;

    return (
      <div
        style={{
          display: 'inline-block',
          width: '120px',
          height: '40px',
          padding: '12px',
          fontSize: '16px',
          color: isGreenText ? 'green' : '#333',
          background: isGreenText? '#b7eeffff' : 'white',
          fontWeight: isGreenText ? 'bold' : 'normal',
          border: '2px solid #339fc0ff',
          textAlign: 'center',
          verticalAlign: 'middle',
        }}
      >
        {props.data?.value}
      </div>
    );
  }}
/>
}

    </div>
  );
}

export default App;
