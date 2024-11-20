
import { Button, Modal, Tooltip } from "antd";

export default function SourcesModal({ sources, open, setOpen }) {
  
  return (
    <Modal
      title="Sources"
      open={open}
      onCancel={() => setOpen(false)}
      footer={null}
    >
      {sources?.map((link, index) => (
        <div key={index} style={{ marginBottom: 8 }}>
          <Tooltip title={link}>
            <Button href={link} target="_blank" rel="noreferrer">
              {`${index+1} - ${link.slice(0, 60)}...`}
            </Button>
          </Tooltip>
        </div>
      ))}

      {sources?.length === 0 && <p>No sources found.</p>}
    </Modal>
  );
}
