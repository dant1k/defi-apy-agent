# QA Acceptance Checklist

## ✅ Completed Items

### 1. Health and Metrics Endpoints
- ✅ `/health` endpoint with database and Redis connection checks
- ✅ `/metrics` endpoint with data counts (dexes, pools, metrics)

### 2. Job Logging
- ✅ Readable job logs with timestamps
- ✅ Duration tracking for jobs
- ✅ Error logging with stack traces
- ✅ Success messages with counts

### 3. UI Works on Last Saved Data
- ✅ All API endpoints return data from database
- ✅ Warning flag when data is stale (>1 hour for DEXes, >10 minutes for pools)
- ✅ UI displays data even if external providers are down
- ✅ Graceful error handling in frontend

### 4. Data Provider Fallback
- ✅ If DefiLlama/Dexscreener fail, API returns cached/stale data from database
- ✅ Warning flag indicates stale data to users
- ✅ No crashes when external APIs are unavailable

## Testing Instructions

### Test with External Providers Disabled

1. **Stop external API calls** (modify providers to return empty/error)
2. **Verify UI still works**:
   - Navigate to `/terminal/aptos/dex`
   - Should show DEXes from database
   - Should show warning if data is stale
3. **Check logs**:
   - Job logs should show errors but continue
   - No crashes in application

### Test Health Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Metrics
curl http://localhost:8000/metrics
```

### Test Job Logs

```bash
# View API logs
docker compose -f docker-compose.terminal.yml logs -f api

# Should see:
# [JOB] [2024-12-20T10:00:00] Starting refresh_dexes job
# [JOB] [2024-12-20T10:00:05] Successfully refreshed 10 DEXes in 5.23s
```

## Acceptance Criteria

- [x] Health endpoint returns status of all services
- [x] Metrics endpoint shows data counts
- [x] Job logs are readable with timestamps
- [x] UI works when external providers are down
- [x] Warning flags show when data is stale
- [x] No crashes on API errors
- [x] All endpoints return proper error responses

