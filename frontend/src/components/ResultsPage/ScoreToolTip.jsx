import React from "react";
import { Card, Typography, Tag } from "antd";

const { Title, Text } = Typography;

export default function ScoreToolTip(scores) {
  const { binary_score, linkert_score, hallucination_score } = scores;

  const areAllScoresNull = () => {
    return (
      binary_score === null &&
      linkert_score === null &&
      hallucination_score === null
    );
  };

  // Function to get Tag color based on score
  const getBinaryTag = (score) => {
    if (score === null) return <Tag color="default">N/A</Tag>;
    return score === 0 ? (
      <Tag color="red">Not Useful</Tag>
    ) : (
      <Tag color="green">Useful</Tag>
    );
  };

  const getHallucinationTag = (score) => {
    if (score === null) return <Tag color="default">N/A</Tag>;
    return score === 0 ? (
      <Tag color="green">No</Tag>
    ) : (
      <Tag color="red">Yes</Tag>
    );
  };

  const getLinkertTag = (score) => {
    if (score === null) return <Tag color="default">N/A</Tag>;
    const linkert_score = parseInt(score);
    const color_score = {
      1: "red",
      2: "orange",
      3: "yellow",
      4: "green",
      5: "green",
    };
    return <Tag style={{fontSize: 12}} color={color_score[linkert_score]}>{linkert_score}/5</Tag>;
  };

  return (
    <Card
      style={{ height: 160, width: 230, borderRadius: 8, padding: 0 }}
      bordered
    >
      <Title level={4} style={{ margin: 0, padding: 0 }}>
        Score Breakdown
      </Title>
      {areAllScoresNull() ? (
        <h2>Click on refresh to evaluate</h2>
      ) : (
        <>
          <div style={{ marginBottom: 2 }}>
            <Text strong>Binary: </Text>
            {getBinaryTag(binary_score)}
          </div>
          <div style={{ marginBottom: 2 }}>
            <Text strong>Linkert: </Text>
            {getLinkertTag(linkert_score)}
          </div>
          <div>
            <Text strong>Hallucination: </Text>
            {getHallucinationTag(hallucination_score)}
          </div>
        </>
      )}
    </Card>
  );
}
