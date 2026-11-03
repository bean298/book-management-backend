-- Schema: book | Table: books

-- Data taken from the project's full dump (00_book_management_seed.sql).
-- Runs automatically the first time the db container initialises and is safe
-- to re-run thanks to ON CONFLICT (id) DO NOTHING.

-- 1. Create books table
CREATE TABLE IF NOT EXISTS book.books (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title           VARCHAR(255) NOT NULL,
    published_year  INTEGER,
    author_id       UUID NOT NULL REFERENCES book.authors(id),
    category_id     UUID NOT NULL REFERENCES book.categories(id),
    cover_image     VARCHAR(255),
    price           DOUBLE PRECISION NOT NULL,
    quantity        INTEGER NOT NULL DEFAULT 0,
    description     TEXT,
    slug            VARCHAR(255) NOT NULL UNIQUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ,
    object_status   VARCHAR(20) NOT NULL DEFAULT 'active'
);

-- 2. Seed books
INSERT INTO book.books (id, title, published_year, author_id, category_id, cover_image, price, quantity, description, slug, created_at, updated_at, object_status)
VALUES
    ('019ff957-18e9-7d85-9131-1ac1b5f2b9de', 'Odyssey', 2003, '019ff40e-abc9-7cab-aedf-ed54aa912aad', '019ff40f-f057-7307-b95d-5c945138b7c9', 'books/019ff957-18e9-7d85-9131-1ac1b5f2b9de/TheOdyssey.jpg', 200000, 0, 'Hành trình trở về quê hương đầy gian nan của người anh hùng Odysseus.', 'odyssey', '2026-08-13 04:17:42.633433+00', '2026-10-19 05:28:56.677955+00', 'active'),
    ('01a18673-1e70-7e76-8853-d128a107198c', 'The Godfather', 1969, '01a18670-2049-7ebd-9daa-a06aa22179ef', '01a1866f-b3a7-7db4-8524-0e0bb7865010', 'books/01a18673-1e70-7e76-8853-d128a107198c/the_god_father.png', 200000, 10, 'Một tiểu thuyết tội phạm về gia đình Corleone và thế giới tội phạm có tổ chức tại Mỹ.', 'the-godfather', '2026-10-29 06:57:33.808799+00', '2026-10-29 07:05:38.150348+00', 'active'),
    ('01a18680-3aa1-7a13-8348-ee3abe41efb2', 'Sự Im Lặng Của Bầy Cừu', 1988, '01a1867c-3fde-7431-a561-ff5c9586d8a3', '01a1866f-b3a7-7db4-8524-0e0bb7865010', 'books/01a18680-3aa1-7a13-8348-ee3abe41efb2/the_silence_of_the_lamb.jpg', 180000, 10, 'Clarice Starling, một thực tập sinh FBI, tìm kiếm sự giúp đỡ từ Hannibal Lecter – một bác sĩ tâm thần đang ngồi tù và cũng là một kẻ giết người hàng loạt – để bắt giữ một tên sát nhân hàng loạt khác có biệt danh là Buffalo Bill.', 'su-im-lang-cua-bay-cuu', '2026-10-29 07:11:52.993178+00', '2026-10-29 07:11:53.031177+00', 'active'),
    ('01a18681-5868-77f7-800e-fc85fcc93206', 'Hannibal', 1999, '01a1867c-3fde-7431-a561-ff5c9586d8a3', '01a1866f-b3a7-7db4-8524-0e0bb7865010', 'books/01a18681-5868-77f7-800e-fc85fcc93206/hannibal.jpg', 190000, 5, 'Tiến sĩ Hannibal Lecter sống tại Florence, trong khi đặc vụ FBI Clarice Starling bị cuốn vào một cuộc truy đuổi đầy nguy hiểm liên quan đến Lecter và quá khứ của ông ta.', 'hannibal', '2026-10-29 07:13:06.152324+00', '2026-10-29 07:13:06.165885+00', 'active'),
    ('01a18684-1b5f-706a-aafb-60b18a5137d0', 'Dune', 1965, '01a18682-9b4f-7e9b-910f-cc7e5a5611d0', '01a1866c-ae91-7126-a786-add7e89dbf43', 'books/01a18684-1b5f-706a-aafb-60b18a5137d0/dune.jpg', 200000, 20, 'Lấy bối cảnh trên hành tinh sa mạc Arrakis, *Dune* theo chân Paul Atreides khi gia đình cậu bị cuốn vào cuộc tranh giành quyền lực, chính trị và loại hương dược quý giá có tên là "melange".', 'dune', '2026-10-29 07:16:07.135245+00', '2026-10-29 07:16:07.193174+00', 'active'),
    ('01a18686-56b9-7b34-9fb7-fc16e9df9277', 'Kính Vạn Hoa', 1995, '019ff407-0a21-7375-8d1f-9492c16927b2', '019ff40f-80ed-7ab7-8119-cae23a32603f', 'books/01a18686-56b9-7b34-9fb7-fc16e9df9277/kinh_van_hoa.jpg', 150000, 5, 'Một bộ sách thiếu nhi Việt Nam của Nguyễn Nhật Ánh, theo chân Quỳnh, Hạnh và Tiểu Long trải qua cuộc sống học đường, tình bạn, những tình huống hài hước cùng các chuyến phiêu lưu.', 'kunh-van-hoa', '2026-10-29 07:18:33.40151+00', '2026-10-29 07:18:33.431659+00', 'active'),
    ('01a18687-8973-7dfe-b208-2d7850b0f1ad', 'Mắt Biếc', 1990, '019ff407-0a21-7375-8d1f-9492c16927b2', '019ff40f-80ed-7ab7-8119-cae23a32603f', 'books/01a18687-8973-7dfe-b208-2d7850b0f1ad/mat_biec.jpg', 100000, 5, 'Một tiểu thuyết Việt Nam của Nguyễn Nhật Ánh, kể về Ngạn – một chàng trai với tình yêu bền bỉ dành cho Hà Lan, thứ tình cảm đã định hình cuộc đời anh từ thuở ấu thơ cho đến khi trưởng thành.', 'mat-biec', '2026-10-29 07:19:51.923379+00', '2026-10-29 07:19:51.972676+00', 'active'),
    ('019ff94f-c8eb-7859-a2fd-01242bb555ac', 'Tôi Thấy Hoa Vàng Trên Cỏ Xanh', 2010, '019ff407-0a21-7375-8d1f-9492c16927b2', '019ff40f-80ed-7ab7-8119-cae23a32603f', 'books/019ff94f-c8eb-7859-a2fd-01242bb555ac/toi thay hoa vang tren co xanh.jpg', 85000, 41, 'Câu chuyện tuổi thơ trong trẻo của cậu bé Thiều và em gái Tường ở một vùng quê nghèo.', 'toi-thay-hoa-vang-tren-co-xanh', '2026-08-13 04:09:43.40336+00', '2026-10-10 08:34:14.071731+00', 'active'),
    ('019ff937-6f5f-7711-b1bc-da1238855ee7', 'Harry Potter và Hòn Đá Phù Thủy', 1998, '019ff407-21d7-72e7-b614-ab4ccd892a33', '019ff40d-6868-7ab0-a64d-504c3eafecbb', 'books/019ff937-6f5f-7711-b1bc-da1238855ee7/Harry_Potter_và_Hòn_đá_phù_thủy_bìa_2003.jpeg', 150000, 4, 'Tập đầu tiên của bộ truyện huyền thoại về cậu bé phù thủy Harry Potter.', 'harry-potter-va-hon-ya-phu-thuy', '2026-08-13 03:43:07.615211+00', '2026-10-11 13:54:56.49238+00', 'active'),
    ('019ff956-369c-7694-89f4-532746a69320', 'Harry Potter và Tên Tù Nhân Ngục Azkaban', 1999, '019ff407-0a21-7375-8d1f-9492c16927b2', '019ff40f-80ed-7ab7-8119-cae23a32603f', 'books/019ff956-369c-7694-89f4-532746a69320/harry_potter_va_ten_tu_nhan.jpg', 155000, 15, 'Tên tù nhân Sirius Black vượt ngục và Harry dần khám phá ra sự thật về quá khứ.', 'harry-potter-va-ten-tu-nhan-nguc-azkaban', '2026-08-13 04:16:44.700707+00', '2026-10-11 13:54:56.494632+00', 'active'),
    ('019ff954-b9a9-78a5-9d24-54bd5fefdda4', 'Harry Potter và Phòng Chứa Bí Mật', 1998, '019ff407-0a21-7375-8d1f-9492c16927b2', '019ff40f-80ed-7ab7-8119-cae23a32603f', 'books/019ff954-b9a9-78a5-9d24-54bd5fefdda4/harry_potter_phong_chua_bi_mat.jpg', 150000, 12, 'Harry trở lại Hogwarts và đối mặt với bí ẩn về căn phòng chứa bí mật.', 'harry-potter-va-phong-chua-bu-mat', '2026-08-13 04:15:07.177864+00', '2026-10-11 13:54:56.499304+00', 'active')
ON CONFLICT (id) DO NOTHING;
