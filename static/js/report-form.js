/* Report submission form: drag-and-drop uploads, image preview, submit loading state. */
document.addEventListener("DOMContentLoaded", () => {
  setupFileDrop("docDrop", "documentInput", "docDropLabel");
  setupFileDrop("imgDrop", "imageInput", "imgDropLabel", handleImagePreview);
  setupSubmitState();
});

function setupFileDrop(dropId, inputId, labelId, onFileSelected) {
  const dropZone = document.getElementById(dropId);
  const input = document.getElementById(inputId);
  const label = document.getElementById(labelId);
  if (!dropZone || !input) return;

  const updateLabel = () => {
    if (input.files && input.files.length > 0) {
      label.textContent = input.files[0].name;
    }
    if (onFileSelected) onFileSelected(input.files[0]);
  };

  input.addEventListener("change", updateLabel);

  ["dragenter", "dragover"].forEach((evt) => {
    dropZone.addEventListener(evt, (e) => {
      e.preventDefault();
      dropZone.classList.add("dragover");
    });
  });

  ["dragleave", "drop"].forEach((evt) => {
    dropZone.addEventListener(evt, (e) => {
      e.preventDefault();
      dropZone.classList.remove("dragover");
    });
  });

  dropZone.addEventListener("drop", (e) => {
    if (e.dataTransfer.files.length) {
      input.files = e.dataTransfer.files;
      updateLabel();
    }
  });
}

function handleImagePreview(file) {
  const preview = document.getElementById("imagePreview");
  if (!preview || !file) return;
  const reader = new FileReader();
  reader.onload = (e) => {
    preview.src = e.target.result;
    preview.style.display = "block";
  };
  reader.readAsDataURL(file);
}

function setupSubmitState() {
  const form = document.getElementById("reportForm");
  const btn = document.getElementById("submitBtn");
  if (!form || !btn) return;

  form.addEventListener("submit", () => {
    btn.disabled = true;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Analyzing with AI...';
  });
}
