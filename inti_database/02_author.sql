-- Schema: book | Table: authors

-- Data taken from the project's full dump (00_book_management_seed.sql).
-- Runs automatically the first time the db container initialises and is safe
-- to re-run thanks to ON CONFLICT (id) DO NOTHING.

-- 1. Create schema book
CREATE SCHEMA IF NOT EXISTS book;

-- 2. Create authors table
CREATE TABLE IF NOT EXISTS book.authors (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(255) NOT NULL,
    bio             TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ,
    object_status   VARCHAR(20) NOT NULL DEFAULT 'active'
);

-- 3. Seed authors
INSERT INTO book.authors (id, name, bio, created_at, updated_at, object_status)
VALUES
    ('019ff407-0a21-7375-8d1f-9492c16927b2', 'Nguyễn Nhật Ánh', 'Nhà văn Việt Nam nổi tiếng với các tác phẩm viết cho tuổi thơ và tuổi trẻ như Kính Vạn Hoa, Tôi Thấy Hoa Vàng Trên Cỏ Xanh.', '2026-08-12 03:32:09.889632+00', NULL, 'active'),
    ('019ff407-21d7-72e7-b614-ab4ccd892a33', 'J.K. Rowling', 'Tác giả người Anh, nổi tiếng toàn cầu với bộ truyện Harry Potter.', '2026-08-12 03:32:15.95993+00', NULL, 'active'),
    ('019ff407-402e-725c-a1c7-1063fe8822c6', 'Nguyễn Du', 'Đại thi hào dân tộc Việt Nam, tác giả của Truyện Kiều.', '2026-08-12 03:32:23.726665+00', NULL, 'active'),
    ('019ff407-586a-73c0-bde9-c1d125966c4d', 'Tô Hoài', 'Nhà văn Việt Nam với tác phẩm Dế Mèn Phiêu Lưu Ký kinh điển.', '2026-08-12 03:32:29.930087+00', NULL, 'active'),
    ('019ff40e-abc9-7cab-aedf-ed54aa912aad', 'Homer', 'Thi sĩ huyền thoại Hy Lạp cổ đại, tác giả của hai bộ sử thi vĩ đại Iliad và Odyssey, đặt nền móng cho văn học phương Tây.', '2026-08-12 03:40:30.025902+00', NULL, 'active'),
    ('01a18670-2049-7ebd-9daa-a06aa22179ef', 'Mario Puzo', 'Tiểu thuyết gia người Mỹ gốc Ý, nổi tiếng nhất với tác phẩm *Bố già* cùng các câu chuyện về Mafia.', '2026-10-29 06:54:17.673114+00', NULL, 'active'),
    ('01a1867c-3fde-7431-a561-ff5c9586d8a3', 'Thomas Harris', 'Tiểu thuyết gia người Mỹ, nổi tiếng nhất với các tác phẩm giật gân tội phạm xoay quanh nhân vật Hannibal Lecter, bao gồm *Red Dragon*, *The Silence of the Lambs*, *Hannibal* và *Hannibal Rising*.', '2026-10-29 07:07:32.190315+00', '2026-10-29 07:08:09.033015+00', 'active'),
    ('01a18682-9b4f-7e9b-910f-cc7e5a5611d0', 'Frank Herbert', 'Nhà văn người Mỹ chuyên về khoa học viễn tưởng, nổi tiếng nhất với loạt tiểu thuyết Dune.', '2026-10-29 07:14:28.815214+00', NULL, 'active')
ON CONFLICT (id) DO NOTHING;
