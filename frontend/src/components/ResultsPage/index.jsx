import { useEffect, useState } from "react";
import api from "../../api";
import {
  Spin,
  theme,
  message,
  Input,
  Button,
  Tooltip,
  Popconfirm,
  Checkbox,
} from "antd";
import {
  EditOutlined,
  InfoCircleOutlined,
  RedoOutlined,
  LinkOutlined,
} from "@ant-design/icons";
import { useNavigate } from "react-router-dom";
import "./styles.css";
import ScoreToolTip from "./ScoreToolTip";
const { TextArea } = Input;

const highlightColors = {
  0: "#FFEB3B", // Yellow
  1: "#FFCDD2", // Red
  2: "#C8E6C9", // Green
  3: "#BBDEFB", // Blue
  4: "#D1C4E9", // Purple
  5: "#FFE0B2", // Orange
};

export default function ResultsPage({ jobId }) {
  const navigate = useNavigate();
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [feedback, setFeedback] = useState({});
  const [draftFeedback, setDraftFeedback] = useState("");
  const [questionLoading, setQuestionLoading] = useState({});
  const [questionEdit, setQuestionEdit] = useState({});
  const [hasRefreshedQuestions, setHasRefreshedQuestions] = useState(false);
  const [sourceOpen, setSourceOpen] = useState({});
  const [showPopconfirm, setShowPopconfirm] = useState(false);
  const [saveInDB, setSaveInDB] = useState(false);

  const parseTextDraftResponse = (text) => {
    const parts = text.split(/(\*\*[^*]+\*\*)/g);
    return parts.map((part, index) => {
      if (part.match(/\*\*[^*]+\*\*/)) {
        return <mark key={index}>{part.slice(2, -2)}</mark>;
      }
      return part;
    });
  };

  const parseTextOrignalMail = (text, substringsToHighlight) => {
    const escapeRegExp = (string) => {
      return string.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    };
    let highlightIndex = 0; // Track index for assigning highlight colors

    let parts = [text]; // Initial parts array with the whole text

    substringsToHighlight.forEach((substring) => {
      const escapedSubstring = escapeRegExp(substring.trim());
      const regex = new RegExp(escapedSubstring, "gi");

      parts = parts.flatMap((part) => {
        if (typeof part !== "string") {
          return [part]; // Non-string parts (e.g., <mark> elements) are left unchanged
        }

        // Split the part by the regex and interleave with highlighted matches
        const splitParts = [];
        let lastIndex = 0;
        part.replace(regex, (match, index) => {
          splitParts.push(part.slice(lastIndex, index)); // Add text before match
          const color =
            highlightColors[
              highlightIndex % Object.keys(highlightColors).length
            ];
          highlightIndex++;
          splitParts.push(
            <mark style={{ backgroundColor: color }} key={highlightIndex}>
              {match}
            </mark>
          ); // Add highlighted match
          lastIndex = index + match.length; // Update last index
          return match;
        });
        splitParts.push(part.slice(lastIndex)); // Add remaining text after last match

        return splitParts;
      });
    });

    return <div>{parts}</div>;
  };

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

  useEffect(() => {
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
      setHasRefreshedQuestions(false);
      message.success("Feedback submitted successfully!");
      const newDraftBody = await api.drafts.updateDrafts(jobId, feedback);
      console.log(newDraftBody);
      setResults((prev) => ({
        ...prev,
        draft_result: {
          ...prev.draft_result,
          body: newDraftBody,
        },
      }));
      message.success("Draft updated successfully!");
      setDraftFeedback("");
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
      setQuestionLoading((prev) => ({
        ...prev,
        [index]: true,
      }));

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
      setFeedback((prev) => ({
        ...prev,
        [index]: "",
      }));
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

  const handleReviewNewAnswer = async (index, answerId) => {
    setQuestionLoading((prev) => ({
      ...prev,
      [index]: true,
    }));

    try {
      await api.answers.reviewAnswer(answerId, feedback[index]);
      fetchResults();
      message.success("Answer reviewed successfully!");
    } catch (err) {
      message.error("Failed to review answer. Please try again.");
    } finally {
      setQuestionLoading((prev) => ({
        ...prev,
        [index]: false,
      }));
    }
  };

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
        <div className="draft-body">
          {" "}
          {results && results?.extracts_to_highlight
            ? parseTextOrignalMail(
                results?.email?.body,
                results?.extracts_to_highlight
              )
            : results?.email?.body}
        </div>
      </div>

      {/* <div
        style={{
          background: colorBgContainer,
          minHeight: 280,
          padding: 24,
          borderRadius: borderRadiusLG,
          marginBottom: 24,
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
              results.answers_questions.map((answerQuestion, index) => (
                <div key={index} className="question-container">
                  <div>
                    <h2
                      style={{ backgroundColor: highlightColors[index] }}
                    >{`Question ${index + 1}: ${answerQuestion.question}`}</h2>
                    {questionEdit[index] ? (
                      <TextArea
                        rows={4}
                        style={{
                          height: `${
                            answerQuestion.answer.split("\n").length * 30
                          }px`,
                          marginBottom: 16,
                        }}
                        value={answerQuestion.answer}
                        onChange={(e) =>
                          setResults((prev) => ({
                            ...prev,
                            answers_questions: prev.answers_questions.map(
                              (item) =>
                                item.answer_id === answerQuestion.answer_id
                                  ? { ...item, answer: e.target.value }
                                  : item
                            ),
                          }))
                        }
                      />
                    ) : (
                      <div>
                        <div>{answerQuestion.answer}</div>
                      </div>
                    )}
                    <div className="source-links">
                      <Tooltip>
                        <div
                          style={{
                            display: "flex",
                            justifyContent: "end",
                            margin: 10,
                          }}
                        >
                          {answerQuestion?.unique_sources && (
                            <Button
                              icon={<LinkOutlined />}
                              size={"medium"}
                              onClick={() =>
                                setSourceOpen((prev) => ({
                                  ...prev,
                                  [index]: !prev[index],
                                }))
                              }
                            >
                              Source
                            </Button>
                          )}
                        </div>
                        {sourceOpen[index] && (
                          <div>
                            {answerQuestion?.unique_sources &&
                              answerQuestion.unique_sources.map(
                                (source, index) => (
                                  <div key={index}>
                                    <a
                                      href={source}
                                      target="_blank"
                                      rel="noreferrer"
                                    >
                                      {source}
                                    </a>
                                  </div>
                                )
                              )}
                          </div>
                        )}
                      </Tooltip>
                      {!questionEdit[index] && (
                        <Tooltip placement="top" title="Edit answer">
                          <Button
                            icon={<EditOutlined />}
                            size={"medium"}
                            type={questionEdit[index] ? "primary" : "default"}
                            onClick={() => handleQuestionEdit(index)}
                          />
                        </Tooltip>
                      )}
                    </div>
                  </div>
                  <TextArea
                    disabled={Object.values(questionLoading).some(
                      (value) => value === true
                    )}
                    rows={4}
                    placeholder="Tell Swiftmail what to change in the answer..."
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
                    <div style={{ display: "flex", alignItems: "center" }}>
                      <Button
                        type="primary"
                        onClick={() =>
                          handleSubmitQuestionFeedback(
                            index,
                            answerQuestion.answer_id
                          )
                        }
                        disabled={Object.values(questionLoading).some(
                          (value) => value === true
                        ) || !feedback[index]?.trim().length}
                      >
                        Regenerate answer
                      </Button>
                      <Tooltip
                        placement="top"
                        title={ScoreToolTip(answerQuestion?.scores)}
                      >
                        <>
                          {Object.values(answerQuestion?.scores).every(
                            (value) => value === null
                          ) ? (
                            <Button
                              icon={<RedoOutlined />}
                              size={"medium"}
                              style={{ marginLeft: 10 }}
                              onClick={() =>
                                handleReviewNewAnswer(
                                  index,
                                  answerQuestion.answer_id
                                )
                              }
                              disabled={Object.values(questionLoading).some(
                                (value) => value === true
                              )}
                            >
                              Review
                            </Button>
                          ) : (
                            <Button
                              icon={<InfoCircleOutlined />}
                              size={"medium"}
                              style={{ marginLeft: 10 }}
                              disabled={Object.values(questionLoading).some(
                                (value) => value === true
                              )}
                            />
                          )}
                        </>
                      </Tooltip>
                    </div>
                    {questionLoading[index] && (
                      <Spin size="small" style={{ marginLeft: 10 }} />
                    )}
                  </div>
                </div>
              ))
            ) : (
              <div>No questions available.</div>
            )}
          </>
        )}
      </div> */}

      {results?.draft_result && (
        <div
          style={{
            background: colorBgContainer,
            padding: 24,
            borderRadius: borderRadiusLG,
          }}
        >
          <h1>Generated Draft</h1>
          <div style={{ position: "relative" }}>
            {hasRefreshedQuestions && (
              <Button
                type="primary"
                size="large"
                onClick={() => handleSubmitDraftFeedback(true)}
                style={{
                  marginTop: 24,
                  backgroundColor: "#00dd00",
                  position: "absolute",
                  zIndex: 999,
                  top: `calc(30% + 24px)`,
                  right: `calc(50% - 50px)`,
                }}
              >
                Refresh Draft
              </Button>
            )}
            <div
              className={`draft-body ${
                hasRefreshedQuestions ? "draft-blur" : ""
              }`}
              style={{ pointerEvents: hasRefreshedQuestions ? "none" : "auto" }}
            >
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
                    parseTextDraftResponse(results.draft_result.body)
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
                {!questionLoading?.draft && (
                  <Tooltip title="Edit draft">
                    <Button
                      icon={<EditOutlined />}
                      size={"large"}
                      onClick={() => handleQuestionEdit("draft")}
                    />
                  </Tooltip>
                )}
              </div>
            </div>
          </div>
          <div className="draft-feedback-container">
            <TextArea
              disabled={questionLoading?.draft}
              rows={4}
              className="draft-feedback"
              placeholder="Tell Swiftmail what to change in the draft..."
              value={draftFeedback}
              onChange={(e) => setDraftFeedback(e.target.value)}
            />
          </div>
          <Button
            type="primary"
            onClick={() => handleSubmitDraftFeedback(false)}
            style={{ marginTop: 24 }}
            disabled={draftFeedback?.trim().length === 0}
          >
            Submit Draft Feedback
          </Button>
        </div>
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
