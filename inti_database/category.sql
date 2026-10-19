-- Schema: book | Table: categories

-- 1. Create schema book
CREATE SCHEMA IF NOT EXISTS book;

-- 2. Create categories table
CREATE TABLE IF NOT EXISTS book.categories (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(255) NOT NULL,
    description     TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ,
    object_status   VARCHAR(20) NOT NULL DEFAULT 'active'
);

-- 3. Seed categories
INSERT INTO book.categories (id, name, description, created_at, object_status)
VALUES
    ('019ff40d-22f7-772a-96a2-17393d65a7aa', 'Tiểu thuyết', 'Các tác phẩm văn học hư cấu dài tập, khai thác nhân vật và cốt truyện phức tạp.', '2026-08-12 10:38:49.463327+07', 'active'),
    ('019ff40d-41aa-7ff5-8b98-1cb91deee46d', 'Lịch sử', 'Sách ghi lại và phân tích các sự kiện, nhân vật lịch sử trong quá khứ.', '2026-08-12 10:38:57.323022+07', 'active'),
    ('019ff40d-6868-7ab0-a64d-504c3eafecbb', 'Trinh thám', 'Thể loại tập trung vào điều tra tội phạm, bí ẩn và phá án.', '2026-08-12 10:39:07.240327+07', 'active'),
    ('019ff40d-7f25-7a63-9ae9-ad43093ae868', 'Truyện ngắn', 'Tập hợp các câu chuyện ngắn với dung lượng nhỏ gọn, tập trung vào một tình huống hoặc khoảnh khắc.', '2026-08-12 10:39:13.061999+07', 'active'),
    ('019ff40f-80ed-7ab7-8119-cae23a32603f', 'Thiếu nhi', 'Sách dành cho trẻ em với nội dung giáo dục, giải trí và hình ảnh minh họa.', '2026-08-12 10:41:24.589731+07', 'active'),
    ('019ff40f-f057-7307-b95d-5c945138b7c9', 'Sử thi', 'Thể loại văn học cổ đại kể về các anh hùng và sự kiện trọng đại, như Iliad, Odyssey của Homer.', '2026-08-12 10:41:53.111824+07', 'active')
ON CONFLICT (id) DO NOTHING;