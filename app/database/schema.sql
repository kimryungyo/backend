-- =============================================================
-- 재난 경보 알림 앱 DB 스키마
-- =============================================================

-- -------------------------------------------------------------
-- 1. users
-- -------------------------------------------------------------
CREATE TABLE users (
    user_id         VARCHAR(36)                     NOT NULL,
    kakao_id        VARCHAR(64)                     NOT NULL,
    role            ENUM('guardian', 'protected')   NOT NULL,
    connection_code CHAR(6)                         NOT NULL,
    name            VARCHAR(50)                     NOT NULL,
    created_at      DATETIME                        NOT NULL,
    PRIMARY KEY (user_id),
    UNIQUE KEY uq_users_kakao_id        (kakao_id),
    UNIQUE KEY uq_users_connection_code (connection_code)
);

-- -------------------------------------------------------------
-- 2. protected_profiles
-- -------------------------------------------------------------
CREATE TABLE protected_profiles (
    user_id                      VARCHAR(36)  NOT NULL,
    region_code                  VARCHAR(20)  NOT NULL,
    auto_location_share_enabled  TINYINT(1)   NOT NULL DEFAULT 0,
    updated_at                   DATETIME     NOT NULL,
    PRIMARY KEY (user_id),
    CONSTRAINT fk_protected_profiles_user FOREIGN KEY (user_id) REFERENCES users (user_id)
);

-- -------------------------------------------------------------
-- 3. protected_profile_categories
-- -------------------------------------------------------------
CREATE TABLE protected_profile_categories (
    user_id   VARCHAR(36)                                                   NOT NULL,
    category  ENUM('elderly', 'dementia', 'mobility_limited', 'hearing_impaired') NOT NULL,
    PRIMARY KEY (user_id, category),
    CONSTRAINT fk_protected_profile_categories_user FOREIGN KEY (user_id) REFERENCES protected_profiles (user_id)
);

-- -------------------------------------------------------------
-- 4. guardian_profiles
-- -------------------------------------------------------------
CREATE TABLE guardian_profiles (
    user_id      VARCHAR(36)  NOT NULL,
    phone_number VARCHAR(20)  NULL,
    updated_at   DATETIME     NOT NULL,
    PRIMARY KEY (user_id),
    CONSTRAINT fk_guardian_profiles_user FOREIGN KEY (user_id) REFERENCES users (user_id)
);

-- -------------------------------------------------------------
-- 5. connection_requests
-- -------------------------------------------------------------
CREATE TABLE connection_requests (
    request_id        VARCHAR(36)                                       NOT NULL,
    requester_user_id VARCHAR(36)                                       NOT NULL,
    target_user_id    VARCHAR(36)                                       NOT NULL,
    status            ENUM('pending', 'accepted', 'rejected', 'canceled') NOT NULL DEFAULT 'pending',
    created_at        DATETIME                                          NOT NULL,
    responded_at      DATETIME                                          NULL,
    PRIMARY KEY (request_id),
    KEY idx_connection_requests_requester (requester_user_id),
    KEY idx_connection_requests_target    (target_user_id),
    CONSTRAINT fk_connection_requests_requester FOREIGN KEY (requester_user_id) REFERENCES users (user_id),
    CONSTRAINT fk_connection_requests_target    FOREIGN KEY (target_user_id)    REFERENCES users (user_id)
);

-- -------------------------------------------------------------
-- 6. guardian_protected_connections
-- -------------------------------------------------------------
CREATE TABLE guardian_protected_connections (
    connection_id     VARCHAR(36) NOT NULL,
    guardian_user_id  VARCHAR(36) NOT NULL,
    protected_user_id VARCHAR(36) NOT NULL,
    created_at        DATETIME    NOT NULL,
    PRIMARY KEY (connection_id),
    UNIQUE KEY uq_guardian_protected (guardian_user_id, protected_user_id),
    KEY idx_gpc_protected (protected_user_id),
    CONSTRAINT fk_gpc_guardian  FOREIGN KEY (guardian_user_id)  REFERENCES users (user_id),
    CONSTRAINT fk_gpc_protected FOREIGN KEY (protected_user_id) REFERENCES users (user_id)
);

-- -------------------------------------------------------------
-- 7. safety_schedules
-- -------------------------------------------------------------
CREATE TABLE safety_schedules (
    schedule_id       VARCHAR(36) NOT NULL,
    guardian_user_id  VARCHAR(36) NOT NULL,
    protected_user_id VARCHAR(36) NOT NULL,
    enabled           TINYINT(1)  NOT NULL DEFAULT 1,
    grace_minutes     INT         NOT NULL,
    updated_at        DATETIME    NOT NULL,
    PRIMARY KEY (schedule_id),
    KEY idx_safety_schedules_guardian  (guardian_user_id),
    KEY idx_safety_schedules_protected (protected_user_id),
    CONSTRAINT fk_safety_schedules_guardian  FOREIGN KEY (guardian_user_id)  REFERENCES users (user_id),
    CONSTRAINT fk_safety_schedules_protected FOREIGN KEY (protected_user_id) REFERENCES users (user_id)
);

-- -------------------------------------------------------------
-- 8. safety_schedule_times
-- -------------------------------------------------------------
CREATE TABLE safety_schedule_times (
    schedule_id VARCHAR(36) NOT NULL,
    check_time  TIME        NOT NULL,
    PRIMARY KEY (schedule_id, check_time),
    CONSTRAINT fk_safety_schedule_times_schedule FOREIGN KEY (schedule_id) REFERENCES safety_schedules (schedule_id)
);

-- -------------------------------------------------------------
-- 9. safety_check_records
-- -------------------------------------------------------------
CREATE TABLE safety_check_records (
    record_id         VARCHAR(36)                                 NOT NULL,
    protected_user_id VARCHAR(36)                                 NOT NULL,
    status            ENUM('safe', 'not_responded', 'help_requested') NOT NULL,
    checked_at        DATETIME                                    NOT NULL,
    PRIMARY KEY (record_id),
    KEY idx_safety_check_records_user (protected_user_id),
    CONSTRAINT fk_safety_check_records_user FOREIGN KEY (protected_user_id) REFERENCES users (user_id)
);

-- -------------------------------------------------------------
-- 10. location_requests
-- -------------------------------------------------------------
CREATE TABLE location_requests (
    request_id        VARCHAR(36)                                               NOT NULL,
    guardian_user_id  VARCHAR(36)                                               NOT NULL,
    protected_user_id VARCHAR(36)                                               NOT NULL,
    status            ENUM('pending', 'approved', 'rejected', 'auto_shared', 'expired') NOT NULL DEFAULT 'pending',
    requested_at      DATETIME                                                  NOT NULL,
    expires_at        DATETIME                                                  NOT NULL,
    PRIMARY KEY (request_id),
    KEY idx_location_requests_guardian  (guardian_user_id),
    KEY idx_location_requests_protected (protected_user_id),
    CONSTRAINT fk_location_requests_guardian  FOREIGN KEY (guardian_user_id)  REFERENCES users (user_id),
    CONSTRAINT fk_location_requests_protected FOREIGN KEY (protected_user_id) REFERENCES users (user_id)
);

-- -------------------------------------------------------------
-- 11. location_share_records  (GeoLocation 통합)
-- -------------------------------------------------------------
CREATE TABLE location_share_records (
    share_id          VARCHAR(36)    NOT NULL,
    guardian_user_id  VARCHAR(36)    NOT NULL,
    protected_user_id VARCHAR(36)    NOT NULL,
    reason            VARCHAR(50)    NOT NULL,
    shared_at         DATETIME       NOT NULL,
    -- GeoLocation 필드
    latitude          DOUBLE         NOT NULL,
    longitude         DOUBLE         NOT NULL,
    accuracy_meters   DOUBLE         NULL,
    address           VARCHAR(255)   NULL,
    captured_at       DATETIME       NOT NULL,
    PRIMARY KEY (share_id),
    KEY idx_location_share_records_guardian  (guardian_user_id),
    KEY idx_location_share_records_protected (protected_user_id),
    CONSTRAINT fk_location_share_records_guardian  FOREIGN KEY (guardian_user_id)  REFERENCES users (user_id),
    CONSTRAINT fk_location_share_records_protected FOREIGN KEY (protected_user_id) REFERENCES users (user_id)
);

-- -------------------------------------------------------------
-- 12. notifications
-- -------------------------------------------------------------
CREATE TABLE notifications (
    notification_id   VARCHAR(36)                                                                                                         NOT NULL,
    receiver_user_id  VARCHAR(36)                                                                                                         NOT NULL,
    notification_type ENUM('connection_request', 'safety_check_request', 'safety_not_responded', 'checklist_not_done', 'help_request', 'location_request', 'disaster_alert') NOT NULL,
    title             VARCHAR(100)                                                                                                        NOT NULL,
    body              TEXT                                                                                                                 NOT NULL,
    created_at        DATETIME                                                                                                            NOT NULL,
    sent_at           DATETIME                                                                                                            NULL,
    PRIMARY KEY (notification_id),
    KEY idx_notifications_receiver (receiver_user_id),
    CONSTRAINT fk_notifications_receiver FOREIGN KEY (receiver_user_id) REFERENCES users (user_id)
);

-- -------------------------------------------------------------
-- 13. disaster_events
-- -------------------------------------------------------------
CREATE TABLE disaster_events (
    event_id      VARCHAR(36)  NOT NULL,
    disaster_type VARCHAR(50)  NOT NULL,
    region_code   VARCHAR(20)  NOT NULL,
    alert_level   VARCHAR(20)  NOT NULL,
    started_at    DATETIME     NOT NULL,
    ended_at      DATETIME     NULL,
    PRIMARY KEY (event_id),
    KEY idx_disaster_events_region  (region_code),
    KEY idx_disaster_events_active  (region_code, ended_at)
);

-- -------------------------------------------------------------
-- 14. checklist_records
-- -------------------------------------------------------------
CREATE TABLE checklist_records (
    record_id          VARCHAR(36) NOT NULL,
    protected_user_id  VARCHAR(36) NOT NULL,
    disaster_event_id  VARCHAR(36) NOT NULL,
    checklist_rule_id  VARCHAR(36) NOT NULL,
    completed_at       DATETIME    NOT NULL,
    PRIMARY KEY (record_id),
    KEY idx_checklist_records_user  (protected_user_id),
    KEY idx_checklist_records_event (disaster_event_id),
    CONSTRAINT fk_checklist_records_user  FOREIGN KEY (protected_user_id) REFERENCES users (user_id),
    CONSTRAINT fk_checklist_records_event FOREIGN KEY (disaster_event_id) REFERENCES disaster_events (event_id)
);

-- -------------------------------------------------------------
-- 15. help_request_records
-- -------------------------------------------------------------
CREATE TABLE help_request_records (
    request_id       VARCHAR(36) NOT NULL,
    protected_user_id VARCHAR(36) NOT NULL,
    guardian_user_id  VARCHAR(36) NOT NULL,
    location_share_id VARCHAR(36) NOT NULL,
    requested_at      DATETIME   NOT NULL,
    PRIMARY KEY (request_id),
    KEY idx_help_request_records_protected (protected_user_id),
    KEY idx_help_request_records_guardian  (guardian_user_id),
    CONSTRAINT fk_help_request_records_protected     FOREIGN KEY (protected_user_id) REFERENCES users (user_id),
    CONSTRAINT fk_help_request_records_guardian      FOREIGN KEY (guardian_user_id)  REFERENCES users (user_id),
    CONSTRAINT fk_help_request_records_location_share FOREIGN KEY (location_share_id) REFERENCES location_share_records (share_id)
);
