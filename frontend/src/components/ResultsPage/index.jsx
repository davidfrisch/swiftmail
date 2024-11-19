import { useEffect, useState } from "react";
import api from "../../api";
import { message, Button, Popconfirm, Checkbox } from "antd";
import { useNavigate } from "react-router-dom";
import "./styles.css";
import OriginalEmail from "./OriginalEmail";
import GeneratedDraft from "./GeneratedDraft";

export default function ResultsPage({ jobId }) {
  const navigate = useNavigate();
  const [results, setResults] = useState(null);
  const [showPopconfirm, setShowPopconfirm] = useState(false);
  const [saveInDB, setSaveInDB] = useState(false);

  const fetchResults = async () => {
    try {
      const res = await api.results.getResults(jobId);
      setResults(res);
    } catch (err) {
      message.error("Failed to load results.");
    }
  };

  useEffect(() => {
    fetchResults();
  }, [jobId]);

  const handleSaveAndConfirm = async () => {
    try {
      await api.enquiries.saveAndConfirm(
        results.email.id,
        jobId,
        results.draft_result.body,
        results.answers_questions,
        saveInDB
      );
      message.success("Draft saved successfully!");
      setShowPopconfirm(false);
      navigate("/mails");
    } catch (err) {
      message.error("Failed to save draft. Please try again.");
    }
  };

  return (
    <div>
      <OriginalEmail email={results?.email} />

      {results?.draft_result && (
        <GeneratedDraft results={results} setResults={setResults} />
      )}
      <div style={{ display: "flex", justifyContent: "center", marginTop: 24 }}>
        <Popconfirm
          title={() => (
            <div style={{ width: 300 }}>
              <h3> Save and confirm the answers? </h3>
              <div style={{ display: "flex", justifyContent: "end" }}>
                <Checkbox
                  onChange={(e) => setSaveInDB(e.target.checked)}
                  checked={saveInDB}
                >
                  Save in database
                </Checkbox>
              </div>
            </div>
          )}
          onConfirm={handleSaveAndConfirm}
          open={showPopconfirm}
          onCancel={() => setShowPopconfirm(false)}
          okText="Yes"
          cancelText="Cancel"
        >
          <Button
            type="primary"
            style={{ backgroundColor: "green" }}
            onClick={() => setShowPopconfirm(true)}
          >
            Confirm and Save
          </Button>
        </Popconfirm>
      </div>
    </div>
  );
}
