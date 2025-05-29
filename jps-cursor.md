1. Organize the top-level fields in the manifest file in the following order (if they exist): jpsType or type, jpsVersion, id, name, categories, logo, homepage, description,
then baseUrl, followed by globals.

2. Convert the following formats baseUrl: https://raw.githubusercontent.com/ORG/REPO/BRANCH or baseUrl: https://github.com/ORG/REPO/blob/BRANCH to this format baseUrl: https://cdn.jsdelivr.net/gh/ORG/REPO@BRANCH

3. Add cdnUrl: https://cdn.jsdelivr.net/gh as the first item under the globals: section if not exists and section exist.

4. Replace all https://raw.githubusercontent.com/ORG/REPO/BRANCH and https://github.com/ORG/REPO/blob/BRANCH URLs with {globals.cdnUrl}/ORG/REPO@BRANCH/...,
only if the organization is jelastic or jelastic-jps and the URL is not inside the mixins: section.

5. In all nested files, replace https://raw.githubusercontent.com/ORG/REPO/BRANCH and https://github.com/ORG/REPO/blob/BRANCH URLs with https://cdn.jsdelivr.net/gh/ORG/REPO@BRANCH/..., but only if the organization is jelastic or jelastic-jps, and the URL is not inside a mixins: block.
