# Gamification API Documentation

## Overview

Gamification APIs support student XP, level progression, badges, challenges, and leaderboards.

All requests require the `X-Tenant-Slug` header to resolve the tenant context.

## Endpoints

### GET /api/v1/students/{student_id}/gamification

Returns the current gamification profile for a student.

Permissions

- `students.read`

Response

- `200 OK` with a `GamificationProfileRead` object.
- `404 Not Found` when the student does not exist in the current tenant.

### POST /api/v1/students/{student_id}/gamification/award

Awards XP to a student and updates their level and streak.

Permissions

- `students.manage`

Request body

- `amount`: number of XP points to award.
- `activity_type`: string representing the activity type.
- `source`: string representing the source or context.
- `note`: optional comment describing the award.

Response

- `200 OK` with the updated `GamificationProfileRead`.

### POST /api/v1/students/{student_id}/gamification/challenges/{challenge_code}/complete

Marks a student challenge as complete and awards challenge XP.

Permissions

- `students.manage`

Request body

- `evidence`: free-form evidence metadata.
- `comment`: optional comment for the completion.

Response

- `200 OK` with a `StudentChallengeRead` object.

### GET /api/v1/students/gamification/leaderboard

Returns the gamification leaderboard for the tenant.

Permissions

- `students.read`

Query parameters

- `limit`: optional integer between 1 and 100 (default 20).

Response

- `200 OK` with a list of `LeaderboardEntryRead` objects.
