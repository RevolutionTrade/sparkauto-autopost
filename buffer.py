"""Client minimal de l'API Buffer (GraphQL, https://api.buffer.com)."""
import json
import time
import urllib.request
import urllib.error

API = "https://api.buffer.com"

CREATE = """mutation CreatePost($input: CreatePostInput!) {
  createPost(input: $input) {
    ... on PostActionSuccess { post { id dueAt } }
    ... on MutationError { message }
  }
}"""


class BufferError(Exception):
    pass


class Buffer:
    def __init__(self, api_key):
        key = (api_key or "").strip()
        if not key:
            raise SystemExit("Clé Buffer absente : ajoutez le secret BUFFER_API_KEY dans GitHub "
                             "(Settings > Secrets and variables > Actions).")
        if len(key) > 300 or any(c.isspace() or ord(c) > 126 for c in key):
            raise SystemExit("Le secret BUFFER_API_KEY ne contient pas une clé Buffer valide "
                             f"({len(key)} caractères, avec des espaces ou des accents). "
                             "Recréez une clé dans Buffer (Settings > API > New Key) et collez-la seule dans ce secret.")
        self.key = key

    def gql(self, query, variables=None, retries=3):
        body = json.dumps({"query": query, "variables": variables or {}}).encode()
        for attempt in range(retries):
            req = urllib.request.Request(API, data=body, method="POST", headers={
                "Authorization": f"Bearer {self.key}", "Content-Type": "application/json",
                "User-Agent": "sparkauto-autopost/1.0"})
            try:
                with urllib.request.urlopen(req, timeout=60) as r:
                    data = json.loads(r.read().decode())
            except urllib.error.HTTPError as e:
                txt = e.read().decode(errors="ignore")
                if e.code == 429 and attempt < retries - 1:
                    time.sleep(int(e.headers.get("Retry-After", "30")))
                    continue
                raise BufferError(f"HTTP {e.code} : {txt[:500]}")
            except urllib.error.URLError as e:
                if attempt < retries - 1:
                    time.sleep(5)
                    continue
                raise BufferError(f"Réseau : {e}")
            if data.get("errors"):
                raise BufferError("; ".join(x.get("message", str(x)) for x in data["errors"]))
            return data["data"]
        raise BufferError("Échec après plusieurs tentatives")

    def channels(self):
        orgs = self.gql("query { account { organizations { id name } } }")["account"]["organizations"]
        out = []
        for o in orgs:
            q = "query($id: OrganizationId!) { channels(input: {organizationId: $id}) { id name displayName service isQueuePaused } }"
            try:
                chs = self.gql(q, {"id": o["id"]})["channels"]
            except BufferError:
                q2 = 'query { channels(input: {organizationId: "%s"}) { id name displayName service isQueuePaused } }' % o["id"]
                chs = self.gql(q2)["channels"]
            for c in chs:
                c["organizationId"] = o["id"]
                out.append(c)
        return out

    def create_post(self, channel_id, service, text, image_url, due_at_iso, draft=False):
        inp = {"text": text, "channelId": channel_id, "schedulingType": "automatic",
               "mode": "customScheduled", "dueAt": due_at_iso,
               "assets": [{"image": {"url": image_url}}]}
        if service == "instagram":
            inp["metadata"] = {"instagram": {"type": "post", "shouldShareToFeed": True}}
        if draft:
            inp["saveToDraft"] = True
        try:
            res = self.gql(CREATE, {"input": inp})["createPost"]
        except BufferError as e:
            msg = str(e)
            # tolérance : si un champ optionnel n'est pas reconnu, on réessaie sans
            if "saveToDraft" in msg and draft:
                # jamais de publication en mode test : on s'arrête proprement
                raise BufferError("Le mode brouillon n'est pas accepté par l'API Buffer : test interrompu sans rien publier. " + msg)
            elif "shouldShareToFeed" in msg:
                inp["metadata"] = {"instagram": {"type": "post"}}
                res = self.gql(CREATE, {"input": inp})["createPost"]
            else:
                raise
        if res.get("message") and not res.get("post"):
            raise BufferError(res["message"])
        return res["post"]
