# Candidacy Admin API (MVP+)

All endpoints return JSON. Authentication uses **JWT Bearer** tokens.  
Errors follow `{ "code": STRING, "message": STRING }`.

## Permissions
- **Admins** (`is_staff` OR in Group `"admin"`): read + write
- **Officers** (in Group `"officer"`): read-only
- **Others**: no access

---

## Current Election
**GET** `/api/elections/current` → **200**
```json
{ "id": 1, "title": "...", "startDate": "YYYY-MM-DD", "endDate": "YYYY-MM-DD", "electionStatus": true, "numWinners": 1 }
```
If none open → **404**
```json
{ "code": "NOT_FOUND", "message": "No open election." }
```

---

## List / Create by Election

### List
**GET** `/api/elections/{id}/candidacies` → **200**
```json
{
  "election": { "id": 1, "title": "..." },
  "results": [
    {
      "id": 123,
      "position_id": 1,
      "position_title": "President",
      "candidate_user_id": 17,
      "candidate_name": "Last, First",
      "credentials": "BSCS",
      "status": true
    }
  ]
}
```
> Note: `position_id`/`position_title`, `credentials`, `status` may be `null`/omitted depending on your model fields.

### Create (Admin-only)
**POST** `/api/elections/{id}/candidacies`
```json
{ "candidateUserId": 17, "positionId": 3, "credentials": "BSCS", "status": true }
```
**201** → created object  
**400** `{ "code": "VALIDATION_ERROR", ... }`  
**403** `{ "code": "FORBIDDEN" }`  
**409** `{ "code": "ALREADY_EXISTS" }`

**Uniqueness**
- If **no** Position FK: unique on `(election, candidate_user)`
- If Position FK exists: unique on `(election, position, candidate_user)`

---

## Update / Delete

### Update (Admin-only)
**PATCH** `/api/candidacies/{cid}`
```json
{ "credentials": "BSCS, Cum Laude", "status": true, "positionId": 3 }
```
→ **200** updated object.

### Delete (Admin-only)
**DELETE** `/api/candidacies/{cid}`
- **204** No Content
- **409** `{ "code": "HAS_VOTES", "message": "Cannot delete candidacy with recorded votes." }`

---

## Quick Create (optional)
**POST** `/api/elections/{id}/candidacies/quick`
```json
{ "name": "Dela Cruz, Juan", "email": "jc@example.com", "positionId": 3, "credentials": "", "status": true }
```
Creates an **inactive** user and a candidacy.  
Email guard: **409** `{ "code": "EMAIL_TAKEN" }`

**201**
```json
{ "user_id": 123, "candidacy_id": 456 }
```
