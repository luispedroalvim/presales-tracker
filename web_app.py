import streamlit as st
import sqlite3
import pandas as pd

# --- Database Management ---
DB_FILE = "opportunities.db"


def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
              CREATE TABLE IF NOT EXISTS opportunities
              (
                  id
                  INTEGER
                  PRIMARY
                  KEY,
                  scope
                  TEXT,
                  client
                  TEXT,
                  description
                  TEXT,
                  price
                  REAL,
                  status
                  TEXT
              )
              """)
    conn.commit()
    conn.close()


def add_opportunity(scope, client, description, price, status):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO opportunities (scope, client, description, price, status) VALUES (?, ?, ?, ?, ?)",
              (scope, client, description, price, status))
    conn.commit()
    conn.close()


def get_all_opportunities():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM opportunities", conn)
    conn.close()
    return df


def update_opportunity(id, scope, client, description, price, status):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
              UPDATE opportunities
              SET scope=?,
                  client=?,
                  description=?,
                  price=?,
                  status=?
              WHERE id = ?
              """, (scope, client, description, price, status, id))
    conn.commit()
    conn.close()


def delete_opportunity(id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM opportunities WHERE id=?", (id,))
    conn.commit()
    conn.close()


# --- Configuration Lists ---
SCOPE_OPTIONS = ['Proposta', 'Paper', 'IT Advisory']
STATUS_OPTIONS = ['Em qualificação', 'Em elaboração', 'Entregue', 'Em negociação', 'Ganha', 'Perdida', 'Não avançar']


# --- Main App Interface ---
def main():
    st.set_page_config(page_title="Pre-Sales Tracker", layout="wide")
    init_db()

    st.title("💼 Pre-Sales Opportunity Tracker")

    # --- Sidebar: Add New Opportunity ---
    with st.sidebar:
        st.header("Add New Opportunity")
        new_client = st.text_input("Client Name")
        new_scope = st.selectbox("Scope", SCOPE_OPTIONS)
        new_status = st.selectbox("Status", STATUS_OPTIONS)
        new_price = st.number_input("Price (€)", min_value=0.0, format="%.2f")
        new_desc = st.text_area("Description")

        if st.button("Add Opportunity"):
            if new_client:
                add_opportunity(new_scope, new_client, new_desc, new_price, new_status)
                st.success(f"Added opportunity for {new_client}!")
                st.rerun()  # Refresh the page to show new data
            else:
                st.error("Client Name is required.")

    # --- Main Area: Data View ---
    st.subheader("Current Opportunities")

    df = get_all_opportunities()

    if not df.empty:
        # Format Price Column for display
        df_display = df.copy()
        df_display['price'] = df_display['price'].apply(lambda x: f"€ {x:,.2f}")

        # Display the table (Streamlit makes it sortable by default)
        st.dataframe(df_display, use_container_width=True, hide_index=True)

        # --- Update / Delete Section ---
        st.markdown("---")
        st.subheader("Manage Opportunities")

        col1, col2 = st.columns([1, 2])

        with col1:
            # Select ID to Edit
            opportunity_ids = df['id'].tolist()
            selected_id = st.selectbox("Select ID to Edit/Delete", opportunity_ids)

        if selected_id:
            # Get current data for the selected ID to pre-fill the form
            selected_row = df[df['id'] == selected_id].iloc[0]

            with col2:
                with st.form("update_form"):
                    st.write(f"Editing Opportunity #{selected_id} - {selected_row['client']}")

                    # Layout for edit fields
                    c1, c2 = st.columns(2)
                    edit_scope = c1.selectbox("Scope", SCOPE_OPTIONS, index=SCOPE_OPTIONS.index(selected_row['scope']))
                    edit_status = c2.selectbox("Status", STATUS_OPTIONS,
                                               index=STATUS_OPTIONS.index(selected_row['status']))

                    edit_client = st.text_input("Client Name", value=selected_row['client'])
                    edit_price = st.number_input("Price (€)", value=float(selected_row['price']), min_value=0.0)
                    edit_desc = st.text_area("Description", value=selected_row['description'])

                    # Buttons
                    col_update, col_delete = st.columns(2)
                    submitted_update = col_update.form_submit_button("Update Details", type="primary")
                    submitted_delete = col_delete.form_submit_button("Delete Opportunity", type="secondary")

                    if submitted_update:
                        update_opportunity(selected_id, edit_scope, edit_client, edit_desc, edit_price, edit_status)
                        st.success("Updated successfully!")
                        st.rerun()

                    if submitted_delete:
                        delete_opportunity(selected_id)
                        st.warning("Deleted successfully!")
                        st.rerun()
    else:
        st.info("No opportunities found. Add one using the sidebar.")


if __name__ == "__main__":
    main()
