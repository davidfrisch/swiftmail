import { useEffect, useState } from "react";
import api from "../../api";
import { Breadcrumb, Layout, Spin, theme, message, Input, Button } from "antd";
import "./styles.css";
const { Header, Content, Footer } = Layout;
const { TextArea } = Input;

export default function ResultsPage({ jobId }) {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [feedback, setFeedback] = useState({});
  const [draftFeedback, setDraftFeedback] = useState(""); // State for draft feedback
  const [questionLoading, setQuestionLoading] = useState({}); // State for each question's loading status
  const [hasRefreshedQuestions, setHasRefreshedQuestions] = useState(false);

  const parseText = (text) => {
    const parts = text.split(/(\*\*[^*]+\*\*)/g); // Split the text by **word** pattern
    return parts.map((part, index) => {
      if (part.match(/\*\*[^*]+\*\*/)) {
        // If the part matches the pattern **word**, render it as bold
        return <strong key={index}>{part.slice(2, -2)}</strong>;
      }
      return part; // Otherwise, return the part as is
    });
  };

  useEffect(() => {
    const fetchResults = async () => {
      try {
        setLoading(true);
        const res = await api.results.getResults(jobId);
        setResults(res);
      } catch (err) {
        setError("Failed to load results. Please try again.");
        message.error("Failed to load results.");
      } finally {
        setLoading(false);
      }
    };
    fetchResults();
  }, [jobId]);

  const handleFeedbackChange = (index, value) => {
    setFeedback((prev) => ({
      ...prev,
      [index]: value,
    }));
  };

  const handleSubmitDraftFeedback = async (isRefreshFeedback) => {
    try {
      setQuestionLoading((prev) => ({
        ...prev,
        draft: true,
      }));
      const feedback = isRefreshFeedback ? "" : draftFeedback;
      await api.drafts.updateDrafts(jobId, feedback);
      message.success("Feedback submitted successfully!");
      setHasRefreshedQuestions(false);
    } catch (err) {
      message.error("Failed to submit feedback. Please try again.");
    } finally {
      setQuestionLoading((prev) => ({
        ...prev,
        draft: false,
      }));
    }
  };

  const handleSubmitQuestionFeedback = async (index, answerId) => {
    try {
      // Set loading status for the specific question
      setQuestionLoading((prev) => ({
        ...prev,
        [index]: true,
      }));

      // Call API to submit question feedback
      const res = await api.answers.updateAnswer(answerId, feedback[index]);
      const { message: resMessage, answer } = res;
      setResults((prev) => ({
        ...prev,
        answers_questions: prev.answers_questions.map((item) =>
          item.answer_id === answerId
            ? { ...item, answer: answer.answer_text }
            : item
        ),
      }));

      message.success(resMessage);
      setHasRefreshedQuestions(true);
    } catch (err) {
      console.log(err);
      message.error("Failed to submit feedback. Please try again.");
    } finally {
      setQuestionLoading((prev) => ({
        ...prev,
        [index]: false,
      }));
    }
  };

  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken();

  return (
    <Layout>
      <Header style={{ display: "flex", alignItems: "center" }}>
        <div className="demo-logo" />
      </Header>
      <Content style={{ padding: "0 64px" }}>
        <Breadcrumb style={{ margin: "16px 0" }}>
          <Breadcrumb.Item>Home</Breadcrumb.Item>
          <Breadcrumb.Item>Jobs</Breadcrumb.Item>
          <Breadcrumb.Item>Job</Breadcrumb.Item>
        </Breadcrumb>
        <div
          style={{
            background: colorBgContainer,
            padding: 24,
            borderRadius: borderRadiusLG,
          }}
        >
          <h1>Email</h1>
          <h2>Subject: {results?.email?.subject}</h2>
          <div className="draft-body">{results?.email.body}</div>
        </div>

        <div
          style={{
            background: colorBgContainer,
            minHeight: 280,
            padding: 24,
            borderRadius: borderRadiusLG,
            marginBottom: 24, // Added margin-bottom for spacing
          }}
        >
          {loading ? (
            <Spin size="large" />
          ) : error ? (
            <div className="error-message">{error}</div>
          ) : (
            <>
              <h1>Results</h1>
              {results.answers_questions?.length > 0 ? (
                results.answers_questions.map((extractQuestion, index) => (
                  <div key={index} className="question-container">
                    <h2>{`Question ${index + 1}: ${
                      extractQuestion.question
                    }`}</h2>
                    <div>{extractQuestion.answer}</div>
                    <TextArea
                      disabled={questionLoading[index]}
                      rows={4}
                      placeholder="Provide your feedback here..."
                      value={feedback[index] || ""}
                      onChange={(e) =>
                        handleFeedbackChange(index, e.target.value)
                      }
                      style={{ marginTop: 16 }}
                    />
                    <div style={{ marginTop: 16 }}>
                      <Button
                        type="primary"
                        onClick={() =>
                          handleSubmitQuestionFeedback(
                            index,
                            extractQuestion.answer_id
                          )
                        }
                        disabled={questionLoading[index]} // Disable button during loading
                      >
                        Regenerate answer
                      </Button>
                      {questionLoading[index] && (
                        <Spin
                          size="small"
                          style={{ marginLeft: 10 }} // Add spinner next to the button
                        />
                      )}
                    </div>
                  </div>
                ))
              ) : (
                <div>No questions available.</div>
              )}
            </>
          )}
        </div>

        {results?.draft_result && (
          <div
            style={{
              background: colorBgContainer,
              padding: 24,
              borderRadius: borderRadiusLG,
            }}
          >
            <h1>Generated Draft</h1>
            <h2>Subject: {results.draft_result.subject}</h2>
            <div className="draft-body">
              {" "}
              {questionLoading?.draft ? (
                <Spin size="large" />
              ) : (
                parseText(results.draft_result.body)
              )}
            </div>

            <div className="draft-feedback-container">
              <TextArea
                disabled={questionLoading?.draft}
                rows={4}
                className="draft-feedback"
                placeholder="Provide feedback on the draft here..."
                value={draftFeedback}
                onChange={(e) => setDraftFeedback(e.target.value)}
              />
            </div>
          </div>
        )}

        <Button
          type="primary"
          onClick={() => handleSubmitDraftFeedback(false)}
          style={{ marginTop: 24 }}
        >
          Submit Draft Feedback
        </Button>
        {hasRefreshedQuestions && (
          <Button
            type="primary"
            onClick={() => handleSubmitDraftFeedback(true)}
            style={{ marginTop: 24, backgroundColor: "#00dd00" }}
          >
            Refresh Draft
          </Button>
        )}
      </Content>
      <Footer style={{ textAlign: "center" }}>
        Swiftmail ©{new Date().getFullYear()}
      </Footer>
    </Layout>
  );
}
