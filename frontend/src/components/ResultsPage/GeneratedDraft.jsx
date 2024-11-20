import { Button, Spin, theme, Tooltip, Input, message } from "antd";
import { EditOutlined, LinkOutlined } from "@ant-design/icons";
import { useState } from "react";
import api from "../../api";
import SourcesModal from "./SourcesModal";

export default function GeneratedDraft({ results, setResults }) {
  const { colorBgContainer, borderRadiusLG } = theme;
  const [hasRefreshedQuestions, setHasRefreshedQuestions] = useState(false);
  const [questionLoading, setQuestionLoading] = useState({});
  const [questionEdit, setQuestionEdit] = useState({});
  const [draftFeedback, setDraftFeedback] = useState("");
  const [openSourcesModal, setOpenSourcesModal] = useState(false);

  const { TextArea } = Input;

  const handleQuestionEdit = (index) => {
    setQuestionEdit((prev) => ({
      ...prev,
      [index]: !prev[index],
    }));
  };

  const handleCopyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    message.success("Copied to clipboard!");
  };

  const parseTextDraftResponse = (text) => {
    const parts = text.split(/(\*\*[^*]+\*\*)/g);
    return parts.map((part, index) => {
      if (part.match(/\*\*[^*]+\*\*/)) {
        return <mark key={index}>{part.slice(2, -2)}</mark>;
      }
      return part;
    });
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
      const newDraftBody = await api.drafts.updateDrafts(
        results.job.id,
        feedback
      );
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

  return (
    <div>
      {results?.sources && (
        <SourcesModal
          sources={results?.sources}
          open={openSourcesModal}
          setOpen={setOpenSourcesModal}
        />
      )}
      <div
        style={{
          background: colorBgContainer,
          padding: 24,
          borderRadius: borderRadiusLG,
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between" }}>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
            }}
          >
            <h1>Generated Draft </h1>
            <Button
              type="link"
              size="large"
              onClick={() => setOpenSourcesModal(true)}
              style={{ marginRight: 16 }}
            >
              <LinkOutlined />
            </Button>
          </div>
          <Button
            type="link"
            onClick={() => handleCopyToClipboard(results.draft_result.body)}
          >
            Copy to clipboard
          </Button>
        </div>
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
    </div>
  );
}
