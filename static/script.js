document.getElementById("predict-form").addEventListener("submit", function (e) {
  e.preventDefault();
  const formData = new FormData(this);
  fetch("/predict", {
    method: "POST",
    body: formData
  })
  .then(res => res.json())
  .then(data => {
    document.getElementById("result").innerText = data.result || data.error;
  });
});
