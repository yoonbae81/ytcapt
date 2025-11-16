<!DOCTYPE html>
<html lang="en" data-theme="auto">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Playlist: {{title}}</title>
    <!-- Pico CSS CDN (auto theme) -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@picocss/pico@1.5.11/css/pico.min.css">
</head>
<body>
    <main class="container">
        <!-- article structure for content boxing and consistent padding -->
        <article>
            <hgroup>
                <h1>
                    % if entries:
                        <a href="{{entries[0]['url']}}" target="_blank" rel="noopener noreferrer" style="text-decoration: none;">
                            Playlist: {{title}}
                        </a>
                    % else:
                        Playlist: {{title}}
                    % end
                </h1>
            </hgroup>
            
            <p>Please select a video to process:</p>

            <nav>
                <ul style="display: block; margin: 0; padding: 0;">
                    % for video in entries:
                        % if video['url'] != '#':
                            <li style="display: block; margin: 0; padding: 0;">
                                <a href="?url={{video['url']}}&lang={{lang}}" 
                                   style="display: block; padding: 0.2rem 0; margin: 0; font-size: 0.95rem;">
                                    {{video['title']}}
                                </a>
                            </li>
                        % end
                    % end
                </ul>
            </nav>

            <footer>
                <!-- Back Button -->
                <a href="." role="button" class="secondary">Back to URL Input</a>
            </footer>
        </article>
    </main>
</body>
</html>