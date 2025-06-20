# Fly.io Deployment Checklist

This checklist ensures proper database persistence on Fly.io.

## Prerequisites

- [ ] Fly CLI installed: `curl -L https://fly.io/install.sh | sh`
- [ ] Logged into Fly.io: `flyctl auth login`
- [ ] In the beartrak-search project directory

## Initial Setup (First-time deployment only)

### 1. Create Persistent Volume

```bash
# Create a 1GB volume in the lax region (matches fly.toml)
flyctl volumes create beartrak_data --region lax --size 1
```

**Important**: This volume must be created before the first deployment. The volume name `beartrak_data` matches the `source` in `fly.toml`.

### 2. Deploy Application

```bash
flyctl deploy
```

## Configuration Verification

Verify these settings are correct in `fly.toml`:

- [ ] `[env] BEARTRAK_PRODUCTION_DB = "/data/beartrak.db"`
- [ ] `[mounts] source = 'beartrak_data'`
- [ ] `[mounts] destination = '/data'`

## Database Persistence

The application now uses:
- **Database Location**: `/data/beartrak.db` (inside the Fly.io volume)
- **Volume Mount**: Fly.io volume `beartrak_data` mounted at `/data`
- **Persistence**: Survives machine suspend/wake cycles and deployments

## Testing Persistence

1. Deploy and add some data via the API
2. Suspend the machine: `flyctl scale count 0`
3. Wake the machine: `flyctl scale count 1`
4. Verify data still exists

## Volume Management Commands

```bash
# List all volumes
flyctl volumes list

# Check volume details
flyctl volumes show <volume-id>

# Create backup snapshot (if supported)
flyctl volumes snapshots list

# Extend volume size (if needed)
flyctl volumes extend <volume-id> --size-gb 2
```

## Troubleshooting

### Volume Not Found Error
If you get "volume not found" errors:
```bash
# Check if volume exists
flyctl volumes list

# If missing, create it
flyctl volumes create beartrak_data --region lax --size 1
```

### Database Permission Issues
If the app can't write to the database:
```bash
# SSH into the machine
flyctl ssh console

# Check directory permissions
ls -la /data
```

### Database File Missing After Restart
This indicates the volume isn't properly mounted. Check:
1. Volume exists: `flyctl volumes list`
2. fly.toml has correct mounts configuration
3. Volume is in the same region as the app

## Migration from Previous Setup

If you had an existing deployment without persistent storage:

1. **Backup any important data** (if possible)
2. Create the volume: `flyctl volumes create beartrak_data --region lax --size 1`
3. Deploy with the updated configuration: `flyctl deploy`
4. The database will start empty and need to be repopulated

## Key Changes Made

1. **fly.toml**: Added `[mounts]` section with persistent volume
2. **database.py**: Added directory creation logic for SQLite files
3. **Environment**: Database path changed from `/app/data/beartrak.db` to `/data/beartrak.db`
4. **Dockerfile**: Updated to support both Docker Compose and Fly.io volume paths
