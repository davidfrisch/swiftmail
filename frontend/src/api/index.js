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
  },

  getWorkspaces: async () => {
    const response = await api.get(`workspaces`);
    const workspaces = response.data.map((workspace) => ({
      value: workspace.slug,
      label: workspace.name,
    }));
    return workspaces;
  },
}

const results = {
  getResults: async (jobId) => {
    const response = await api.get(`jobs/${jobId}/results`);
    return response.data;
  },
}


const emails = {

  getNewEmails: async () => {
    const response = await api.get('emails/refresh');

    if (!response.data?.mails) {
      throw new Error('Failed to fetch new mails');
    }

    if (response.data.mails.length === 0) {
      return [];
    }
    return response.data.mails;
  },

  getEmails: async () => {
    const response = await api.get('emails');
    return response.data?.emails;
  },

  getEmail: async (id) => {
    const response = await api.get(`emails/${id}`);
    const { mail, job } = response.data;
    return { ...mail, job };
  },

  createEmail: async (email) => {
    const response = await api.post('emails', email);
    return response.data;
  },

  toggleAsRead: async (emailId) => {
    const response = await api.put(`emails/${emailId}/toggle-read`);
    return response.data;
  },

  saveAndConfirm: async (emailId, jobId, finalDraft, finalAnswers, saveInDatabase) => {
    const response = await api.post(`emails/${emailId}/save-and-confirm`,
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
  getAnswers: async (emailId) => {
    const response = await api.get(`emails/${emailId}/answers`);
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





export default { jobs, results, emails, answers, drafts };

