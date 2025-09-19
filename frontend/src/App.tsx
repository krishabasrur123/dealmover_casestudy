import { useState } from 'react';
import axios from "axios";
import './App.css';

function App() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [selectedDate, setSelectedDate] = useState('');
  const [results, setResults] = useState<{ revenue: string; cost: string } | null>(null);
  const [loading, setLoading] = useState(false); // Loading state

  const onFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSelectedFile(event.target.files?.[0] || null);
  };

  const onDateChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSelectedDate(event.target.value);
  };

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

      setResults({
        revenue: data.revenue || "Error: No Revenue Found",
        cost: data.cos || "Error: No Cost of Sales found",
      });
    } catch (error: any) {
      console.error("Upload error:", error.response?.data || error.message);
      setResults({
        revenue: "Error: No Revenue Found",
        cost: "Error: No Cost of Sales found",
      });
    } finally {
      setLoading(false); // Hide loading
    }
  };

  const revenue = results?.revenue ?? "";
  const cost = results?.cost ?? "";

  return (
    <div>
      <h1>Financial Value Extractor</h1>
      <h3>Please upload the 10-K document and an optional period date</h3>

      <div>
        <input type="file" onChange={onFileChange} />
        <input type="date" onChange={onDateChange} />
        <button onClick={onFileUpload}>Upload!</button>
      </div>

      {/* Loading message */}
      {loading && <p>Processing your file, please wait...</p>}

      {/* Show table only if results exist and not loading */}
      {!loading && results && (
        <table>
          <thead>
            <tr>
              <th>Item</th>
              <th>Value</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Revenue</td>
              <td>{revenue}</td>
            </tr>
            <tr>
              <td>Cost of Sales</td>
              <td>{cost}</td>
            </tr>
            <tr>
              <td>Gross Profit</td>
              <td>
                {Number(revenue) && Number(cost)
                  ? (Number(revenue) - Number(cost)).toLocaleString()
                  : "-"}
              </td>
            </tr>
          </tbody>
        </table>
      )}
    </div>
  );
}

export default App;
