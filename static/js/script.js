var droppedFile = null;
var processedImage = null; 
var historic = [];


$(document).ready(function () {
   

   // Handle drag and drop
   var dropZone = document.getElementById('dropZone');

   dropZone.addEventListener('dragover', function (e) {
       e.preventDefault();
       dropZone.classList.add('dragover');
   });

   dropZone.addEventListener('dragleave', function (e) {
       e.preventDefault();
       dropZone.classList.remove('dragover');
   });

   dropZone.addEventListener('drop', function (e) {
       e.preventDefault();
       dropZone.classList.remove('dragover');

       droppedFile = e.dataTransfer.files[0]; // Store the dropped file
       previewImage(droppedFile);
   });

   // Handle file input change
   $('#imageInput').change(function () {
       droppedFile = this.files[0]; // Store the selected file
       previewImage(droppedFile);
   });

   // Preview the selected image
   function previewImage(file) {
       if (file) {
           var reader = new FileReader();
           reader.onload = function (e) {
               var img = new Image();
               img.src = e.target.result;

               img.onload = function () {
                   var maxWidth = 512; // Set the maximum width
                   var maxHeight = 512; // Set the maximum height

                   var width = img.width;
                   var height = img.height;

                   // Calculate the scaling factor to fit within the defined dimensions
                   var scale = Math.min(maxWidth / width, maxHeight / height);

                   // Set the image dimensions
                   
                   $('#imagePreview').css({
                       'width': width * scale + 'px',
                       'height': height * scale + 'px'
                   });
                   $('.drag-drop').css({
                     'width': width * scale + 'px',
                     'height': height * scale + 'px'
                    });
                   

                   $('#imagePreview').attr('src', e.target.result);
                   $('#imagePreview').css('display', 'block');
                   $('#imageInput').css('display', 'none');
                   
               };
           };
           reader.readAsDataURL(file);
       }
   }

   // Process image button click
   $('#processButton').click(function () {
    if (!processedImage && droppedFile) {
        console.log(" [+] First process, initializing the temp picture")
        // If processedImage is not set (first click), use the original image
        processedImage = droppedFile;
        historic.push(processedImage)
    }

    if (processedImage) {
        // Send the last processed image to the server for further processing
        var formData = new FormData();
        formData.append('file', processedImage);

        $.ajax({
            type: 'POST',
            url: '/process_image',
            data: formData,
            processData: false,
            contentType: false,
            success: function (data) {
                
                fetch('data:image/png;base64,' + data).then(res => res.blob()).then(blob => {
                    console.log(" [+] updating processed image")
                    processedImage = new File([blob], "File name",{ type: "image/png" })
                    historic.push(processedImage)
                    console.log("[+] Added backup",historic)
                })

                // Display the newly processed image
                $('#imagePreview').attr('src', 'data:image/png;base64,' + data);
                $('#imagePreview').css('display', 'block');
            },
            error: function () {
                alert('An error occurred while processing the image.');
            }
        });
    } else {
        alert('Please select an image file.');
    }
});

// Reset button click
$('#resetButton').click(function () {
    // Clear the processed image and reset the file input
    processedImage = droppedFile;
    previewImage(droppedFile);
});

$('#undoButton').click(function () {
    // Check if there is a backup, if yes, restore the previous state
    console.log(" [+] [Undo] ",historic)
    
    if (historic.length > 1) {
        historic.pop(); // Remove the last state from historic
        processedImage = historic[historic.length - 1]; // Get the previous state
        previewImage(processedImage);
    }
});
});

