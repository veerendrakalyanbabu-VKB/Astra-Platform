from astra.core.audit import AuditLogger


def test_audit_logger(tmp_path):
    audit_path = tmp_path / "audit.log"
    audit = AuditLogger(audit_path=audit_path)

    audit.log_execute("OPEN_APP", True)
    audit.log_block("FORMAT_DISK", "too dangerous")

    content = audit_path.read_text(encoding="utf-8")

    assert "EXECUTE" in content
    assert "BLOCK" in content
