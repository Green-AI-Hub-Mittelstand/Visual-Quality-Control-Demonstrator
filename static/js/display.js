console.log(original_image_path)

var hostname = window.location.hostname;
var port = window.location.port;
let original_image = document.getElementById("originalImageField");
original_image.src = "http://" + hostname + ":" + port + "/" + original_image_path;

var heatmap_url = "http://" + hostname + ":" + port + "/results/" + task_id + "/heatmap";
fetch(heatmap_url)
    .then(response => response.json())
    .then(data => {
        console.log(data);
        data.heatmaps.forEach((item, index) => {
            let container = document.createElement("div");
            container.className = "col";

            let title = document.createElement("h3");
            title.textContent = `Image ${index + 1}:`;
            container.appendChild(title);

            let row = document.createElement("div");
            row.className = "row";

            // Column for Text
            let textCol = document.createElement("div");
            textCol.className = "col";
            let scoreParagraph = document.createElement("p");
            scoreParagraph.textContent = `Anomaly Score: ${item.score}`;
            let anomalyParagraph = document.createElement("p");
            anomalyParagraph.textContent = `Detected Anomaly: ${item.classification}`;
            textCol.appendChild(scoreParagraph);
            textCol.appendChild(anomalyParagraph);

            // Column for Image
            let imageCol = document.createElement("div");
            imageCol.className = "col";
            let image = document.createElement("img");
            image.style.minWidth = "100%";
            image.src = 'data:image/jpeg;base64,' + item.heatmap;
            imageCol.appendChild(image);

            row.appendChild(textCol);
            row.appendChild(imageCol);

            container.appendChild(row);

            // Assuming you have a parent element to append this to, for example, a div with id="imagesContainer"
            document.getElementById("imagesContainer").appendChild(container);
        });
    })
    .catch(error => console.error('Error fetching the heatmap:', error));