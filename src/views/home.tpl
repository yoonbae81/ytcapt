<!DOCTYPE html>
<html lang="en" data-theme="auto">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YT Caption Downloader</title>
    <!-- Pico CSS CDN (auto theme) -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@1.5.11/css/pico.min.css">
    <!-- Custom styling for responsiveness and aesthetics -->
    <style>
        .container {
            padding-top: 1em;
            max-width: 768px; /* Use a reasonable max width for readability */
        }
        /* Reduce space between hgroup and article */
        main.container > hgroup {
            margin-bottom: 0;
        }
        main.container > article {
            margin-top: 0;
            padding-top: 2em; 
        }
        .error { 
            border: 1px solid var(--pico-del-color);
            background-color: var(--pico-del-background-color);
            color: var(--pico-del-color);
            padding: var(--pico-spacing);
            border-radius: var(--pico-border-radius);
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
            <form action="{{baseurl}}/" method="POST">
                <fieldset>
                    <label for="url">
                        Video or Playlist URL
                        <input type="text" id="url" name="url" value="{{url}}" required
                               placeholder="https://www.youtube.com/watch?v=...">
                    </label>
                </fieldset>
                
                <fieldset role="group">
                    <label for="lang">
                        Language
                        <select id="lang" name="lang">
                            <option value="ko" {{'selected' if lang == 'ko' else ''}}>Korean</option>
                            <option value="en" {{'selected' if lang == 'en' else ''}}>English</option>
                        </select>
                    </label>
                    <button type="submit">Process</button>
                </fieldset>
            </form>
        </article>

        % if error:
            <div class="error" role="alert">
                <strong>Error:</strong><br>{{error}}
            </div>
        % end
    </main>
</body>
</html>