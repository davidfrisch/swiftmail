import axios from "axios";
import { ANYTHING_LLM } from "../constants.js";


export const api = axios.create({
  baseURL: ANYTHING_LLM,
  headers: {
    "Content-Type": "application/json",
  },
});


const apiAnythingLLM = {
  healthCheck: async () => {
    return api.get("/ping");
  },

  checkToken: async () => {
    try {
      await api.get("/v1/auth");
      return { data: { message: "Token is valid" } };
    } catch (error) {
      return { data: { message: error.response.data.error } };
    }
  },

  setToken: async (token) => {
    api.defaults.headers.common["Authorization"] = `Bearer ${token}`;
    return await apiAnythingLLM.checkToken();
  },

  getFolders: async () => {
    const res = await api.get("/v1/documents");
    return res.data?.localFiles?.items || [];
  },

  getWorkspaces: async () => {
    const res = await api.get("/v1/workspaces");
    return res.data?.workspaces || [];
  },

  addNewUrlToWorkspace: async (workspace, url) => {
    // Add to folder
    const payload = {
      "link": url
    }

    const res1 = await api.post(`workspace/${workspace}/upload-link`, payload);
    const savedUrl = JSON.parse(res1.config.data).link;

    // Add to workspace
    const folders = await apiAnythingLLM.getFolders();

    const folder = folders.find((folder) => folder.name === 'custom-documents');


    const urlFromFolder = folder?.items?.find((item) => {
      return item.chunkSource === "link://" + savedUrl
    });

    const elemToAdd = `custom-documents/` + urlFromFolder.name;

    const payload2 = {
      adds: [elemToAdd],
      deletes: []
    }
    const res = await api.post("workspace/" + workspace + "/update-embeddings", payload2);
    return res;
  },
};


export default apiAnythingLLM;