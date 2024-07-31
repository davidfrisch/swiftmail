import axios from 'axios';
const backendUrl = 'http://localhost:8000';

const api = axios.create({
  baseURL: backendUrl,
});

const jobs = {
  getJobs: async () => {
    const response = await api.get('jobs');
    return response.data;
  },

  getJob: async (id) => {
    const response = await api.get(`jobs/${id}`);
    return response.data;
  },

  createJob: async (job) => {
    const response = await api.post('jobs', job);
    return response.data;
  }
}

const results = {
  getResults: async (jobId) => {
    const response = await api.get(`jobs/${jobId}/results`);
    return response.data;
  },
}


const enquiries = {

  getNewEnquiries: async () => {
    const response = await api.get('enquiries/refresh');
    return response.data;
  },

  getEnquiries: async () => {
    const response = await api.get('enquiries');
    return response.data;
  },

  getEnquiry: async (id) => {
    const response = await api.get(`enquiries/${id}`);
    return response.data;
  },
}

const answers = {
  getAnswers: async (enquiryId) => {
    const response = await api.get(`enquiries/${enquiryId}/answers`);
    return response.data;
  },

  updateAnswer: async (answerId, feedback) => {
    const response = await api.put(`answers/${answerId}`, { feedback });
    return response.data;
  }
}

const drafts = {
  updateDrafts: async (draftId, feedback) => {
    const response = await api.post(`drafts/${draftId}`, { feedback });
    return response.data;
  }
}





export default { jobs, results, enquiries, answers, drafts };

