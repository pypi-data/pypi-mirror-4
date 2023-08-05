-- Unfail(0, now, group, queue, [count])
--
-- Move `count` jobs out of the failed state and into the provided queue

if #KEYS ~= 0 then
    error('Unfail(): Expected 0 KEYS arguments')
end

local now   = assert(tonumber(ARGV[1]), 'Unfail(): Arg "now" missing'  )
local group = assert(ARGV[2]          , 'Unfail(): Arg "group" missing')
local queue = assert(ARGV[3]          , 'Unfail(): Arg "queue" missing')
local count = assert(tonumber(ARGV[4] or 25),
    'Unfail(): Arg "count" not a number: ' .. tostring(ARGV[4]))

-- Get up to that many jobs, and we'll put them in the appropriate queue
local jids = redis.call('lrange', 'ql:f:' .. group, 0, count - 1)

-- Get each job's original number of retries, 
local jobs = {}
for index, jid in ipairs(jids) do
    table.insert(jobs, redis.call('hgetall', 'ql:j:' .. jid))
end

-- And now set each job's state, and put it into the appropriate queue
local toinsert = {}
for index, job in ipairs(jobs) do
    job.history = cjson.decode(job.history or '{}')
    table.insert(job.history, {
        q   = queue,
        put = math.floor(now)
    })
    redis.call('hmset', 'ql:j:' .. job.jid,
        'state'    , 'waiting',
        'worker'   , '',
        'expires'  , 0,
        'queue'    , queue,
        'remaining', job.retries or 5,
        'history'  , cjson.encode(history))
    table.insert(toinsert, job.priority - (now / 10000000000))
    table.insert(toinsert, jid)
end

redis.call('zadd', 'ql:q:' .. queue .. '-work', unpack(toinsert))

-- If we're in the failed state, remove all of our data
redis.call('ltrim', 'ql:f:' .. group, 0, count - 1)
if (redis.call('llen', 'ql:f:' .. group) == 0) then
    redis.call('srem', 'ql:failures', group)
end

return #jids
