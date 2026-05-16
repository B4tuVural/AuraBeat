-- =============================================================
-- AuraBeat — PostgreSQL İlk Kurulum
-- ---------------------------------------------------------
-- Bu script yalnızca container İLK oluşturulduğunda çalışır.
-- (docker-entrypoint-initdb.d/ klasöründe bulunur.)
-- Data volume zaten varsa tekrar çalışmaz — güvenlidir.
-- =============================================================

-- UUID üretimi için PostgreSQL'in yerel uuid-ossp extension'ı
-- Django UUIDField() default=uuid.uuid4 kullanıyor ama bazı
-- sorgu/raporlama senaryolarında DB tarafında da ihtiyaç olabilir.
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- pg_trgm: ileride sanatçı/şarkı adı üzerinde benzerlik araması
-- (trigram search) eklemek istersen altyapısı hazır olsun.
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Doğrulama: encoding ve locale'in doğru geldiğinden emin ol
DO $$
BEGIN
    RAISE NOTICE '================================================';
    RAISE NOTICE 'AuraBeat DB başarıyla oluşturuldu.';
    RAISE NOTICE 'Encoding : %', current_setting('server_encoding');
    RAISE NOTICE 'Timezone : %', current_setting('timezone');
    RAISE NOTICE '================================================';
END
$$;
