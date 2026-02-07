export async function onRequest(context) {
    const url = new URL(context.request.url);
    const path = url.pathname;

    // Regex for /YYYY/MM/DD/slug naming convention, optionally handling /feed/ suffix
    const articleRegex = /^\/\d{4}\/\d{2}\/\d{2}\/([^\/]+)(?:\/feed)?\/?$/;
    const match = path.match(articleRegex);

    if (match) {
        const slug = match[1];
        const newPath = `/blog/${slug}/`;
        return Response.redirect(`${url.origin}${newPath}`, 301);
    }

    return context.next();
}
