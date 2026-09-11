cursor.execute(
    """
    UPDATE trades
    SET
        status=?,
        exit_price=?,
        pnl=?,
        closed_at=?
    WHERE id=?
    """,
    (
        "CLOSED",
        float(exit_price),
        float(pnl),
        datetime.utcnow().isoformat(),
        trade_id
    )
)
