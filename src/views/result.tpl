<!DOCTYPE html>
<html lang="en" data-theme="auto">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- Changed title to English -->
    <title>Result: {{title}}</title>
    <!-- Pico CSS CDN (auto theme) -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@1.5.11/css/pico.min.css">
    
    <!-- Custom styles for button alignment and top padding removal -->
    <style>
        main.container {
            padding-top: 1em;
        }
        main.container > hgroup {
            margin-bottom: 0;
        }
        main.container > article {
            margin-top: 0;
            padding-top: 2em; 
        }
        /* Ensures all items in the footer grid are vertically centered and stretch to uniform height */
        footer.grid {
            align-items: stretch; /* Make all grid items match the height of the tallest item */
        }
        footer.grid > * {
            /* Force the content inside anchor/button tags to be centered */
            display: flex;
            justify-content: center;
            align-items: center;
            /* Ensures both anchor and button elements are rendered with the same box model height */
            height: 100%; 
        }
    </style>
</head>
<body>
    <main class="container">
        <hgroup>
            <h1>YT Caption Downloader</h1>
            <p>Download and refine auto-generated video captions.</p>
        </hgroup>
        <article>
            <p>{{title}}</p>
        
            <!-- Text area shows only the refined caption text -->
            <textarea readonly id="caption-text" rows="15">{{text_content}}</textarea>

            <footer class="grid">
                <!-- Back Button -->
                <a href="." role="button" class="secondary">New URL</a>

                <!-- Action Buttons (Copy and Download) -->
                <button id="copy-btn">Copy Text</button>
                <a href="{{download_url}}" role="button" download>Download .txt</a>
            </footer>
        </article>
    </main>

    <!-- JavaScript for Copy Button functionality -->
    <script>
        document.getElementById('copy-btn').addEventListener('click', function() {
            var textToCopy = document.getElementById('caption-text').value;
            var button = this;
            
            // Use the modern clipboard API
            navigator.clipboard.writeText(textToCopy).then(function() {
                // Success message
                var originalText = button.textContent;
                button.textContent = 'Copied!';
                
                setTimeout(function() {
                    button.textContent = originalText;
                }, 2000);
            }, function(err) {
                // Failure message
                var originalText = button.textContent;
                button.textContent = 'Copy Failed';
                console.error('Failed to copy text: ', err);

                 setTimeout(function() {
                    button.textContent = originalText;
                }, 2000);
            });
        });
    </script>
</body>
</html>