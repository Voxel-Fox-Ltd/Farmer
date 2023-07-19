CREATE TABLE IF NOT EXISTS plots(
    id TEXT NOT NULL PRIMARY KEY DEFAULT (gen_random_uuid()::TEXT),
    owner_id BIGINT NOT NULL,
    guild_id BIGINT NOT NULL,
    position SMALLINT[] NOT NULL,
    type TEXT NOT NULL,
    UNIQUE (owner_id, guild_id, position)
);
CREATE INDEX IF NOT EXISTS plots_owner_id_guild_id_idx
ON plots(owner_id, guild_id);
CREATE INDEX IF NOT EXISTS plots_owner_id_guild_id_idx
ON plots(owner_id, guild_id);


CREATE TABLE IF NOT EXISTS animals(
    id TEXT NOT NULL PRIMARY KEY DEFAULT (gen_random_uuid()::TEXT),
    type TEXT NOT NULL,
    plot_id TEXT NOT NULL REFERENCES plots(id) ON DELETE CASCADE,
    production_rate FLOAT NOT NULL DEFAULT '0.5'
);
CREATE INDEX IF NOT EXISTS animals_plot_id_idx
ON animals(plot_id);


CREATE TABLE IF NOT EXISTS inventory(
    owner_id BIGINT NOT NULL,
    guild_id BIGINT NOT NULL,
    money BIGINT DEFAULT 0,
    PRIMARY KEY (owner_id, guild_id)
);


CREATE TABLE IF NOT EXISTS user_items(
    owner_id BIGINT NOT NULL,
    guild_id BIGINT NOT NULL,
    item TEXT NOT NULL,
    amount INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (owner_id, guild_id, item)
);


CREATE TABLE IF NOT EXISTS plot_items(
    plot_id TEXT NOT NULL REFERENCES plots(id) ON DELETE CASCADE,
    item TEXT NOT NULL,
    amount INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (plot_id, item)
);
