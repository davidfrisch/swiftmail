import { useEffect, useState } from "react";
import api from "../../api";

export default function ResultsPage({ jobId }) {
  const [results, setResults] = useState({});

  useEffect(() => {
    const fetchResults = async () => {
      const res = await api.results.getResults(jobId);
      console.log(res);
      setResults(res);
    };

    fetchResults();
  }, [jobId]);

  return <div>Hello</div>;
}
