import { useEffect, useState } from "react";
import "./App.css";
import apiAnythingLLM from "./api";
import { DownOutlined } from "@ant-design/icons";
import { Dropdown, Space } from "antd";

function App() {
  const [token, setToken] = useState("3WMNAPZ-GYH4RBE-M67SR00-7Y7KYEF");
  const [form, setForm] = useState({
    workspaceName: "",
    url: "",
  });
  const [isLoading, setIsLoading] = useState(false);
  const [folders, setFolders] = useState([]);
  const [message, setMessage] = useState("");

  const handleOnSave = async () => {
    const res = await apiAnythingLLM.setToken(token);
    setMessage(res.data.message);
    const timeout = setTimeout(() => {
      setMessage("");
    }, 2000);

    return () => {
      clearTimeout(timeout);
    };
  };

  const handleOnChange = (key, value) => {
    setForm((prevForm) => ({
      ...prevForm,
      [key]: value,
    }));
  };

  const getFolders = async () => {
    const workspace = await apiAnythingLLM.getWorkspaces();
    const itemWorkspace = workspace.map((folder, i) => ({
      key: "" + i,
      label: (
        <a onClick={(e) => handleOnChange("workspaceName", folder.name)}>
          {folder.name}
        </a>
      ),
    }));
    setFolders(itemWorkspace);
    setForm((prevForm) => ({
      ...prevForm,
      workspaceName: workspace[0]?.name || "No folders",
    }));
  };

  useEffect(() => {
    apiAnythingLLM.setToken(token);
    getFolders();
  }, [token]);

  const handleAddNewUrlToWorkspace = async () => {
    setIsLoading(true);
    try {
      await apiAnythingLLM.addNewUrlToWorkspace(form.workspaceName, form.url);
      setForm((prevForm) => ({
        ...prevForm,
        url: "",
      }));
      setMessage("Url added to workspace");
      setTimeout(() => {
        setMessage("");
      }, 5000);
    } catch (error) {
      setMessage("Error adding url to workspace");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <div>
        <span>Token: </span>
        <input
          type="password"
          value={token}
          onChange={(e) => setToken(e.target.value)}
        />
        <button onClick={handleOnSave}>Save</button>
        <div>
          {folders?.length > 0 && (
            <Dropdown
              menu={{
                items: folders,
              }}
            >
              <a
                onClick={(e) => {
                  e.preventDefault();
                }}
              >
                <Space>
                  {form.workspaceName}
                  <DownOutlined />
                </Space>
              </a>
            </Dropdown>
          )}
          <div>
            <input
              type="text"
              value={form.url}
              onChange={(e) => handleOnChange("url", e.target.value)}
            />
          </div>

          <div>
            <button disabled={isLoading} onClick={handleAddNewUrlToWorkspace}>
              Save
            </button>
          </div>
          <div>{message}</div>
        </div>
      </div>
    </>
  );
}

export default App;
