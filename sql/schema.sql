-- ============================================================================
--  ООО «ТехноСервис» · Физическая модель данных «Управление проектами разработки ПО»
--  Реализация логической модели IDEF1X (практики №5–6), СУБД PostgreSQL 14+.
--
--  Правила отображения IDEF1X -> DDL:
--    * идентифицирующая связь  -> FK входит в PRIMARY KEY potomka, ON DELETE CASCADE;
--    * неидентифицирующая связь-> FK обычный атрибут; обязательная: NOT NULL,
--      необязательная: NULL + ON DELETE SET NULL;
--    * связь 1:1               -> UNIQUE на FK дочерней таблицы;
--    * домены значений         -> CHECK-ограничения (при росте справочников
--                                 выносятся в отдельные таблицы, 3НФ).
-- ============================================================================

BEGIN;

-- ----------------------------------------------------------------------------
-- E1 ЗАКАЗЧИК (независимая сущность)
-- ----------------------------------------------------------------------------
CREATE TABLE customer (
    id_customer     SERIAL          PRIMARY KEY,
    name            VARCHAR(200)    NOT NULL,
    inn             VARCHAR(12),
    customer_type   CHAR(10)        NOT NULL
                        CHECK (customer_type IN ('юрлицо', 'ИП', 'физлицо')),
    contact_person  VARCHAR(120),
    phone           VARCHAR(20),
    email           VARCHAR(120),
    CONSTRAINT uq_customer_inn UNIQUE (inn)
);
COMMENT ON TABLE  customer IS 'Заказчик — независимая сущность IDEF1X (E1)';

-- ----------------------------------------------------------------------------
-- E4 СОТРУДНИК (независимая сущность)
-- ----------------------------------------------------------------------------
CREATE TABLE employee (
    id_employee     SERIAL          PRIMARY KEY,
    full_name       VARCHAR(150)    NOT NULL,
    position        VARCHAR(80)     NOT NULL,
    role            VARCHAR(40)     NOT NULL
                        CHECK (role IN ('аналитик','архитектор','дизайнер','backend','frontend',
                                        'mobile','QA','QA-автоматизатор','DevOps','PM',
                                        'техписатель','юрист','бухгалтер')),
    department      VARCHAR(60)     NOT NULL
                        CHECK (department IN ('разработка','тестирование','продажи',
                                              'бухгалтерия','HR')),
    email           VARCHAR(120)    NOT NULL,
    salary_rate     NUMERIC(10,2),
    CONSTRAINT uq_employee_email UNIQUE (email)
);
COMMENT ON TABLE  employee IS 'Сотрудник — механизм процессов A1–A4 (E4)';

-- ----------------------------------------------------------------------------
-- E2 ПРОЕКТ (зависимая: идентифицирующая связь от customer)
-- ----------------------------------------------------------------------------
CREATE TABLE project (
    id_customer     INT             NOT NULL,
    id_project      INT             NOT NULL,
    name            VARCHAR(200)    NOT NULL,
    start_date      DATE            NOT NULL,
    end_date        DATE,
    budget          NUMERIC(12,2)   CHECK (budget >= 0),
    status          VARCHAR(20)     NOT NULL DEFAULT 'анализ'
                        CHECK (status IN ('анализ','разработка','тестирование',
                                          'внедрение','закрыт')),
    id_manager      INT,
    PRIMARY KEY (id_customer, id_project),
    CONSTRAINT fk_project_customer FOREIGN KEY (id_customer)
        REFERENCES customer (id_customer) ON DELETE CASCADE,          -- идентифицирующая
    CONSTRAINT fk_project_manager  FOREIGN KEY (id_manager)
        REFERENCES employee (id_employee) ON DELETE SET NULL,        -- неидентифицирующая
    CONSTRAINT chk_project_dates   CHECK (end_date IS NULL OR end_date >= start_date)
);
CREATE INDEX ix_project_manager ON project (id_manager);
COMMENT ON TABLE  project IS 'Проект — зависимая сущность (E2), составной PK по IDEF1X';

-- ----------------------------------------------------------------------------
-- E3 ДОГОВОР (независимая; связь 1:1 с проектом, неидентифицирующая)
-- ----------------------------------------------------------------------------
CREATE TABLE contract (
    id_contract     SERIAL          PRIMARY KEY,
    number          VARCHAR(30)     NOT NULL,
    contract_date   DATE            NOT NULL,
    id_project_customer INT         NOT NULL,
    id_project          INT         NOT NULL,
    amount          NUMERIC(12,2)   NOT NULL CHECK (amount >= 0),
    payment_terms   VARCHAR(200),
    status          VARCHAR(20)     NOT NULL DEFAULT 'проект'
                        CHECK (status IN ('проект','подписан','расторгнут','закрыт')),
    CONSTRAINT uq_contract_number UNIQUE (number),
    CONSTRAINT fk_contract_project FOREIGN KEY (id_project_customer, id_project)
        REFERENCES project (id_customer, id_project) ON DELETE CASCADE,
    CONSTRAINT uq_contract_project UNIQUE (id_project_customer, id_project)  -- 1:1
);
COMMENT ON TABLE  contract IS 'Договор (ИП 4): связь 1:1 с проектом, неидентифицирующая (E3)';

-- ----------------------------------------------------------------------------
-- E5 ЗАДАЧА (зависимая от project; неидентифицирующая от employee)
-- ----------------------------------------------------------------------------
CREATE TABLE task (
    id_customer     INT             NOT NULL,
    id_project      INT             NOT NULL,
    id_task         INT             NOT NULL,
    description     TEXT            NOT NULL,
    task_type       VARCHAR(20)     NOT NULL
                        CHECK (task_type IN ('требование','разработка','тест','дефект',
                                             'документ','внедрение')),
    status          VARCHAR(20)     NOT NULL DEFAULT 'открыта'
                        CHECK (status IN ('открыта','в работе','на ревью','на тестировании',
                                          'выполнена','закрыта')),
    priority        CHAR(8)         NOT NULL DEFAULT 'Major'
                        CHECK (priority IN ('Blocker','Critical','Major','Minor')),
    planned_hours   NUMERIC(6,2),
    due_date        DATE,
    id_executor     INT,
    PRIMARY KEY (id_customer, id_project, id_task),
    CONSTRAINT fk_task_project FOREIGN KEY (id_customer, id_project)
        REFERENCES project (id_customer, id_project) ON DELETE CASCADE,  -- идентифицирующая
    CONSTRAINT fk_task_executor FOREIGN KEY (id_executor)
        REFERENCES employee (id_employee) ON DELETE SET NULL             -- неидентифицирующая
);
CREATE INDEX ix_task_executor ON task (id_executor);
COMMENT ON TABLE  task IS 'Задача (ИП 11): зависимая сущность (E5)';

-- ----------------------------------------------------------------------------
-- E6 ТЕСТ_КЕЙС (зависимая от task; неидентифицирующая от employee)
-- ----------------------------------------------------------------------------
CREATE TABLE test_case (
    id_customer     INT             NOT NULL,
    id_project      INT             NOT NULL,
    id_task         INT             NOT NULL,
    id_test_case    INT             NOT NULL,
    name            VARCHAR(200)    NOT NULL,
    steps           TEXT,
    expected_result TEXT            NOT NULL,
    result          VARCHAR(20)     NOT NULL DEFAULT 'не выполнялся'
                        CHECK (result IN ('не выполнялся','пройден','не пройден',
                                          'заблокирован')),
    id_tester       INT,
    checked_at      TIMESTAMP,
    PRIMARY KEY (id_customer, id_project, id_task, id_test_case),
    CONSTRAINT fk_tc_task FOREIGN KEY (id_customer, id_project, id_task)
        REFERENCES task (id_customer, id_project, id_task) ON DELETE CASCADE,  -- идентифицирующая
    CONSTRAINT fk_tc_tester FOREIGN KEY (id_tester)
        REFERENCES employee (id_employee) ON DELETE SET NULL
);
CREATE INDEX ix_tc_tester ON test_case (id_tester);
COMMENT ON TABLE  test_case IS 'Тест-кейс (ИП 17): зависимая сущность (E6)';

-- ----------------------------------------------------------------------------
-- E7 БАГ_РЕПОРТ (зависимая от test_case; неидентифицирующая от employee)
-- ----------------------------------------------------------------------------
CREATE TABLE bug_report (
    id_customer     INT             NOT NULL,
    id_project      INT             NOT NULL,
    id_task         INT             NOT NULL,
    id_test_case    INT             NOT NULL,
    id_bug          INT             NOT NULL,
    description     TEXT            NOT NULL,
    severity        VARCHAR(12)     NOT NULL
                        CHECK (severity IN ('Blocker','Critical','Major','Minor','Trivial')),
    status          VARCHAR(20)     NOT NULL DEFAULT 'открыт'
                        CHECK (status IN ('открыт','в работе','исправлен','на регрессии',
                                          'закрыт','отклонён')),
    id_developer    INT,
    found_at        TIMESTAMP       NOT NULL DEFAULT now(),
    closed_at       TIMESTAMP,
    PRIMARY KEY (id_customer, id_project, id_task, id_test_case, id_bug),
    CONSTRAINT fk_bug_tc FOREIGN KEY (id_customer, id_project, id_task, id_test_case)
        REFERENCES test_case (id_customer, id_project, id_task, id_test_case)
        ON DELETE CASCADE,
    CONSTRAINT fk_bug_dev FOREIGN KEY (id_developer)
        REFERENCES employee (id_employee) ON DELETE SET NULL,
    CONSTRAINT chk_bug_closed CHECK (closed_at IS NULL OR closed_at >= found_at)
);
CREATE INDEX ix_bug_dev ON bug_report (id_developer);
COMMENT ON TABLE  bug_report IS 'Баг-репорт (ИП 17–18, UOB 3 IDEF3): зависимая сущность (E7)';

-- ----------------------------------------------------------------------------
-- E8 ДОКУМЕНТ (независимая; неидентифицирующие связи с project и employee)
-- ----------------------------------------------------------------------------
CREATE TABLE document (
    id_document     SERIAL          PRIMARY KEY,
    doc_type        VARCHAR(30)     NOT NULL
                        CHECK (doc_type IN ('ТЗ','протокол интервью','макет','архитектура',
                                            'API-спецификация','инструкция','акт','счёт',
                                            'договор','отчёт о качестве')),
    name            VARCHAR(200)    NOT NULL,
    url             VARCHAR(500)    NOT NULL,
    version         VARCHAR(10)     NOT NULL DEFAULT 'v1.0',
    doc_date        DATE            NOT NULL,
    id_customer     INT,
    id_project      INT,
    id_author       INT,
    CONSTRAINT fk_doc_project FOREIGN KEY (id_customer, id_project)
        REFERENCES project (id_customer, id_project) ON DELETE SET NULL,
    CONSTRAINT fk_doc_author FOREIGN KEY (id_author)
        REFERENCES employee (id_employee) ON DELETE SET NULL
);
CREATE INDEX ix_doc_project ON document (id_customer, id_project);
CREATE INDEX ix_doc_author  ON document (id_author);
COMMENT ON TABLE  document IS 'Документ (хранилище D2): независимая сущность (E8)';

COMMIT;
