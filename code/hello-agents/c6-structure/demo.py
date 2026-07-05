import streamlit as st
import requests
from datetime import datetime
#bb
# 页面配置
st.set_page_config(page_title="BTC价格监控", page_icon="₿", layout="centered")

def get_btc_price():
    """
    从 CoinGecko API 获取比特币当前价格（USD）及24小时涨跌幅
    返回: (price, change_percent, change_amount)
    """
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_24hr_change=true"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        btc = data.get('bitcoin')
        if not btc:
            raise ValueError("API返回数据格式异常，缺少 'bitcoin' 字段")
        price = btc.get('usd')
        change_percent = btc.get('usd_24h_change')
        if price is None or change_percent is None:
            raise ValueError("API返回数据不完整，缺少价格或涨跌幅")
        change_amount = price * (change_percent / 100.0)
        return price, change_percent, change_amount
    except (requests.RequestException, ValueError, KeyError) as e:
        raise RuntimeError(f"获取价格失败: {e}")

def main():
    # 页面标题和说明
    st.markdown("<h1 style='text-align: center;'>₿ 比特币价格监视器</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>实时查看比特币当前价格与24小时变化趋势</p>", unsafe_allow_html=True)

    # 初始化 session_state
    if 'last_data' not in st.session_state:
        st.session_state.last_data = None
    if 'error' not in st.session_state:
        st.session_state.error = None
    if 'need_refresh' not in st.session_state:
        st.session_state.need_refresh = False

    # 布局：标题左侧留白，右侧放刷新按钮
    col_title, col_btn = st.columns([3, 1])
    with col_title:
        st.write("")  # 仅用于占位，保持居中感
    with col_btn:
        refresh = st.button("🔄 刷新")

    if refresh:
        st.session_state.need_refresh = True

    # 数据获取逻辑
    if st.session_state.need_refresh or st.session_state.last_data is None:
        with st.spinner("正在获取比特币价格..."):
            try:
                price, change_percent, change_amount = get_btc_price()
                st.session_state.last_data = {
                    'price': price,
                    'change_percent': change_percent,
                    'change_amount': change_amount,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                st.session_state.error = None
                st.session_state.need_refresh = False
            except Exception as e:
                st.session_state.error = str(e)
                st.session_state.need_refresh = False
                if st.session_state.last_data is None:
                    st.error("无法获取比特币价格，请检查网络后重试")
                else:
                    st.warning("获取最新价格失败，显示上次数据")

    # 展示数据
    if st.session_state.last_data:
        data = st.session_state.last_data
        price = data['price']
        change_percent = data['change_percent']
        change_amount = data['change_amount']

        # 关键修正：始终使用 normal，让 Streamlit 自动判断正负颜色
        st.metric(
            label="Bitcoin (BTC)",
            value=f"${price:,.2f}",
            delta=f"{change_amount:+.2f}",
            delta_color="normal"  # 修正：删除错误的 "inverse" 逻辑
        )

        # 涨跌幅百分比（手动着色）
        percent_str = f"{change_percent:+.2f}%"
        color = "green" if change_percent >= 0 else "red"
        st.markdown(
            f"<p style='text-align: center; font-size: 1.3em; color: {color};'>24h变化: {percent_str}</p>",
            unsafe_allow_html=True
        )

        # 显示最后更新时间
        if 'timestamp' in data:
            st.caption(f"数据来源: CoinGecko | 最后更新: {data['timestamp']}")

    # 错误提示（仅当完全无数据时显示大错误）
    if st.session_state.error and st.session_state.last_data is None:
        st.error(st.session_state.error)
        st.info("请点击刷新按钮重试")

if __name__ == "__main__":
    main()