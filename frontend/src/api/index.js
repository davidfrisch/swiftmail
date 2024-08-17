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

  createJob: async (emailId) => {
    const response = await api.post('jobs', { email_id: emailId });
    return response.data;
  },

  retryJob: async (emailId) => {
    const response = await api.post('jobs/retry', { email_id: emailId });
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

    if (!response.data?.mails) {
      throw new Error('Failed to fetch new mails');
    }

    if (response.data.mails.length === 0) {
      return [];
    }
    return response.data.mails;
  },

  getEnquiries: async () => {
    const response = await api.get('enquiries');
    return response.data?.mails;
  },

  getEnquiry: async (id) => {
    const response = await api.get(`enquiries/${id}`);
    const { mail, job } = response.data;
    return { ...mail, job };
  },

  toggleAsRead: async (enquiryId) => {
    const response = await api.put(`enquiries/${enquiryId}/toggle-read`);
    return response.data;
  },

  saveAndConfirm: async (enquiryId, jobId, finalDraft, finalAnswers, saveInDatabase) => {
    const response = await api.post(`enquiries/${enquiryId}/save-and-confirm`,
      {
        job_id: jobId,
        draft: finalDraft,
        answers: finalAnswers,
        save_in_db: saveInDatabase,
      }
    );
    return response.data;
  }
}

const answers = {
  getAnswers: async (enquiryId) => {
    const response = await api.get(`enquiries/${enquiryId}/answers`);
    return response.data;
  },

  updateAnswer: async (answerId, feedback) => {
    const response = await api.put(`answers/${answerId}`, { feedback });
    return response.data;
  },

  reviewAnswer: async (answerId) => {
    const response = await api.put(`answers/${answerId}/review`, {});
    return response.data;
  }
}

const drafts = {
  updateDrafts: async (jobId, feedback) => {
    const response = await api.post(`drafts/retry`, { job_id: jobId, feedback });
    return response.data.draft.draft_body;
  }
}





export default { jobs, results, enquiries, answers, drafts };

