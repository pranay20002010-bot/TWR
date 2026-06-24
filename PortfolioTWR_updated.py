    )

    chart["Nifty50 TRI"] = (
        n50["Growth100"]
    )

    chart["Nifty500 TRI"] = (
        n500["Growth100"]
    )
    cash_flow_table = (
        cf.groupby("Date", as_index=False)["Amount"]
        .sum()
        .sort_values("Date")
    )
    inflow_dates = cf.loc[
        cf["Amount"] > 0,
        "Date"
    ].sort_values()
    start_date = (
        inflow_dates.iloc[0]
        if not inflow_dates.empty
        else cf["Date"].min()
    )
    holdings_table = build_current_holdings(
        tx,
        prices,
        ledger.index.max(),
        ledger.iloc[-1]["Cash"]
    )
    market_cap_allocation = build_market_cap_allocation(
        tx,
        prices,
        ledger.index.max()
    )

    st.subheader(f"Start Date: {format_display_date(start_date)}")

    st.subheader(
        "Growth of Portfolio"
    )

    fig = px.line(
        chart,
        x=chart.index,
        y=chart.columns
    )

    st.plotly_chart(fig, use_container_width=True)

    pie_fig = build_market_cap_pie_figure(
        market_cap_allocation
    )
    if pie_fig is not None:
        st.subheader("Market Cap Allocation")
        left_col, center_col, right_col = st.columns([1, 2, 1])
        with center_col:
            st.plotly_chart(
                pie_fig,
                use_container_width=True
            )

    pdf_bytes = build_pdf_report(
        selected_portfolio,
        start_date,
        current_date,
        ledger.iloc[-1]["Portfolio Value"],
        ledger.iloc[-1]["Cash"],
        summary,
        chart,
        cash_flow_table,
        holdings_table,
        market_cap_allocation
    )

    st.download_button(
        "Download PDF Report",
        data=pdf_bytes,
        file_name=f"{selected_portfolio}_PortfolioReport.pdf",
        mime="application/pdf"
    )

    st.subheader("Daily Ledger")

    display = ledger.copy()

    for c in [
        "Equity Value",
        "Cash",
        "Portfolio Value",
        "External Flow"
    ]:
        display[c] = display[c].apply(
            format_inr
        )

    st.dataframe(
        display,
        use_container_width=True
    )

    st.subheader("Current Holdings")

    display_holdings = holdings_table.copy()
    display_holdings["Weight"] = display_holdings["Weight"].map(
        lambda x: f"{x:.2%}" if pd.notna(x) else ""
    )

    def holdings_style(row):
        if row["Ticker"] == "Cash":
            return ["font-weight: bold"] * len(row)
        return [""] * len(row)

    st.dataframe(
        display_holdings.style.apply(
            holdings_style,
            axis=1
        ),
        use_container_width=True,
        hide_index=True
    )

    st.subheader("External Cash Flows")

    display_cf = cash_flow_table.copy()
    display_cf["Date"] = display_cf["Date"].apply(
        format_display_date
    )
    display_cf["Amount"] = display_cf["Amount"].apply(
        format_inr
    )

    st.dataframe(
        display_cf,
        use_container_width=True,
        hide_index=True
    )

else:
    st.info(
        "Upload one workbook with 'Transactions' and 'Cashflows' tabs to begin."
    )
