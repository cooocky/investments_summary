import pandas as pd


def leave_only_stocks_and_bonds(df):
    sb_df = df[(df['Asset Category'] == 'Stocks') | (df['Asset Category'] == 'Bonds')]

    return sb_df


def set_index(df, index_name):
    df = df[df[index_name].notna()]
    df.set_index(keys=index_name, inplace=True)

    return df


def assign_first_row_as_header(df):
    new_header = df.iloc[0]
    df = df.iloc[1:]
    df.columns = new_header

    return df


def get_market_to_market_data(df):
    m2m_df = df[df.iloc[:, 0] == 'Mark-to-Market Performance Summary']
    m2m_df = assign_first_row_as_header(m2m_df)
    m2m_df = leave_only_stocks_and_bonds(m2m_df)
    m2m_df = m2m_df.loc[:, 'Asset Category':'Current Price']
    m2m_df = set_index(m2m_df, 'Symbol')

    return m2m_df


def get_currency_data(df):
    op_df = df[df.iloc[:, 0] == 'Open Positions']
    op_df = assign_first_row_as_header(op_df)
    op_df = leave_only_stocks_and_bonds(op_df)
    currency_df = op_df[['Currency', 'Symbol']]
    currency_df = set_index(currency_df, 'Symbol')

    return currency_df


def get_column_for_dividends(df, column_name):
    col_df = df[df.iloc[:, 0] == column_name]
    col_df = assign_first_row_as_header(col_df)
    col_df = col_df[col_df['Description'].notna()]
    col_df['Symbol'] = col_df['Description'].map(lambda x: x.split('(')[0])
    col_df = set_index(col_df, 'Symbol')

    return col_df


def get_dividends(df):
    div_df = get_column_for_dividends(df, 'Dividends')
    div_tax_df = get_column_for_dividends(df, 'Withholding Tax')
    div_df = pd.to_numeric(div_df['Amount'], errors='coerce') + pd.to_numeric(div_tax_df['Amount'], errors='coerce')
    div_df.rename('Dividends', inplace=True)

    return div_df


def get_data_from_report(filename):
    df = pd.read_csv(filename)
    m2m_df = get_market_to_market_data(df)
    currency_df = get_currency_data(df)
    summary_df = m2m_df.merge(right=currency_df, how='outer', left_index=True, right_index=True)
    div_df = get_dividends(df)
    summary_df = summary_df.merge(right=div_df, how='outer', left_index=True, right_index=True)

    return summary_df


if __name__ == '__main__':
    # TODO:
    # split to classes stocks and bonds
    # split to stocks, bonds and ETFs
    # align all to USD
    # split ETFs to conservatives and mediums
    # enrich with currencies of expired bonds
    # enrich with currencies of sold assets
    # add coupons and dividends
    # change -- to special formulas
    # add the column when the asset was bought
    # not correct split in dividends 'MSFT' and 'MSFT '

    df = get_data_from_report('1.csv')

    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(df)

    df.to_excel('report.xlsx')
