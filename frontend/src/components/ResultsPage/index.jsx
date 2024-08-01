import { useEffect, useState } from "react";
import api from "../../api";
import { Spin, theme, message, Input, Button } from "antd";
import { EditOutlined } from "@ant-design/icons";
import "./styles.css";
const { TextArea } = Input;

export default function ResultsPage({ jobId }) {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [feedback, setFeedback] = useState({});
  const [draftFeedback, setDraftFeedback] = useState("");
  const [questionLoading, setQuestionLoading] = useState({});
  const [questionEdit, setQuestionEdit] = useState({});
  const [hasRefreshedQuestions, setHasRefreshedQuestions] = useState(false);

  const parseText = (text) => {
    const parts = text.split(/(\*\*[^*]+\*\*)/g);
    return parts.map((part, index) => {
      if (part.match(/\*\*[^*]+\*\*/)) {
        return <strong key={index}>{part.slice(2, -2)}</strong>;
      }
      return part;
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

  const handleQuestionEdit = (index) => {
    setQuestionEdit((prev) => ({
      ...prev,
      [index]: !prev[index],
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
    <div>
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
                  <div>
                    <h2>{`Question ${index + 1}: ${
                      extractQuestion.question
                    }`}</h2>
                    {questionEdit[index] ? (
                      <TextArea
                        rows={4}
                        style={{
                          height: `${
                            extractQuestion.answer.split("\n").length * 30
                          }px`,
                          marginBottom: 16,
                        }}
                        value={extractQuestion.answer}
                        onChange={(e) =>
                          setResults((prev) => ({
                            ...prev,
                            answers_questions: prev.answers_questions.map(
                              (item) =>
                                item.answer_id === extractQuestion.answer_id
                                  ? { ...item, answer: e.target.value }
                                  : item
                            ),
                          }))
                        }
                      />
                    ) : (
                      <div>
                        <div>{extractQuestion.answer}</div>
                      </div>
                    )}
                  </div>
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
                  <div
                    style={{
                      marginTop: 16,
                      display: "flex",
                      justifyContent: "space-between",
                    }}
                  >
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
                    <Button
                      icon={<EditOutlined />}
                      size={"medium"}
                      onClick={() => handleQuestionEdit(index)}
                    />
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
              <div>
                {questionEdit["draft"] ? (
                  <TextArea
                    rows={4}
                    style={{
                      height: `${
                        results.draft_result.body.split("\n").length * 30
                      }px`,
                      marginBottom: 16,
                    }}
                    value={results.draft_result.body}
                    onChange={(e) =>
                      setResults((prev) => ({
                        ...prev,
                        draft_result: {
                          ...prev.draft_result,
                          body: e.target.value,
                        },
                      }))
                    }
                  />
                ) : (
                  parseText(results.draft_result.body)
                )}
              </div>
            )}
            <div
              style={{
                display: "flex",
                justifyContent: "end",
                fontSize: "25px",
              }}
            >
              <Button
                icon={<EditOutlined />}
                size={"large"}
                onClick={() => handleQuestionEdit("draft")}
              />
            </div>
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
        </div>
      )}
    </div>
  );
}
