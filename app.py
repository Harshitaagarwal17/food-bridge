"""
FoodBridge - Flask Backend Application
Complete REST API for Food Distribution Management System
"""

from flask import Flask, request, jsonify, render_template
from db_config import get_connection
from datetime import datetime, timedelta
import traceback

app = Flask(__name__)


# ═══════════════════════════════════════════════════════════
# HELPER
# ═══════════════════════════════════════════════════════════

def serialize_row(row):
    """Convert datetime objects in a dict to ISO strings for JSON."""
    if row is None:
        return None
    out = {}
    for k, v in row.items():
        if isinstance(v, datetime):
            out[k] = v.isoformat()
        elif isinstance(v, timedelta):
            out[k] = str(v)
        else:
            out[k] = v
    return out


def serialize_rows(rows):
    return [serialize_row(r) for r in rows]


# ═══════════════════════════════════════════════════════════
# PAGE ROUTES
# ═══════════════════════════════════════════════════════════

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/donor')
def donor_page():
    return render_template('donor.html')


@app.route('/receiver')
def receiver_page():
    return render_template('receiver.html')


@app.route('/admin')
def admin_page():
    return render_template('admin.html')


# ═══════════════════════════════════════════════════════════
# ZONE ROUTES
# ═══════════════════════════════════════════════════════════

@app.route('/api/zones', methods=['GET'])
def get_zones():
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM Zone ORDER BY zone_name")
            zones = cur.fetchall()
        conn.close()
        return jsonify({'success': True, 'data': serialize_rows(zones)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════
# DONOR ROUTES
# ═══════════════════════════════════════════════════════════

@app.route('/api/add_donor', methods=['POST'])
def add_donor():
    try:
        data = request.get_json()
        required = ['donor_name', 'phone', 'email', 'address', 'zone_id']
        for field in required:
            if field not in data or not data[field]:
                return jsonify({'success': False, 'error': f'Missing field: {field}'}), 400

        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO Donor (donor_name, phone, email, address, zone_id)
                    VALUES (%s, %s, %s, %s, %s)
                """, (data['donor_name'], data['phone'], data['email'],
                      data['address'], data['zone_id']))
                conn.commit()
                donor_id = cur.lastrowid
            return jsonify({'success': True, 'donor_id': donor_id, 'message': 'Donor registered successfully!'})
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/add_donation', methods=['POST'])
def add_donation():
    try:
        data = request.get_json()
        required = ['donor_id', 'food_name', 'category', 'quantity', 'unit',
                     'cooked_time', 'expiry_date', 'zone_id']
        for field in required:
            if field not in data or not data[field]:
                return jsonify({'success': False, 'error': f'Missing field: {field}'}), 400

        is_perishable = data.get('is_perishable', True)

        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO FoodItem
                        (donor_id, food_name, category, quantity, unit,
                         is_perishable, cooked_time, expiry_date, status, zone_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'available', %s)
                """, (data['donor_id'], data['food_name'], data['category'],
                      data['quantity'], data['unit'], is_perishable,
                      data['cooked_time'], data['expiry_date'], data['zone_id']))
                conn.commit()
                food_id = cur.lastrowid
            return jsonify({'success': True, 'food_id': food_id, 'message': 'Donation added successfully!'})
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/donor/<int:donor_id>/donations', methods=['GET'])
def get_donor_donations(donor_id):
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT f.*, z.zone_name, z.city,
                       GetUrgencyLevel(f.expiry_date) AS urgency
                FROM FoodItem f
                JOIN Zone z ON f.zone_id = z.zone_id
                WHERE f.donor_id = %s
                ORDER BY f.created_at DESC
            """, (donor_id,))
            donations = cur.fetchall()
        conn.close()
        return jsonify({'success': True, 'data': serialize_rows(donations)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/donation/<int:food_id>/update', methods=['PUT'])
def update_donation(food_id):
    try:
        data = request.get_json()
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                fields = []
                values = []
                allowed = ['food_name', 'category', 'quantity', 'unit',
                           'cooked_time', 'expiry_date', 'is_perishable', 'zone_id']
                for field in allowed:
                    if field in data:
                        fields.append(f"{field} = %s")
                        values.append(data[field])
                if not fields:
                    return jsonify({'success': False, 'error': 'No fields to update'}), 400
                values.append(food_id)
                query = f"UPDATE FoodItem SET {', '.join(fields)} WHERE food_id = %s"
                cur.execute(query, values)
                conn.commit()
            return jsonify({'success': True, 'message': 'Donation updated successfully!'})
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/donation/<int:food_id>/delete', methods=['DELETE'])
def delete_donation(food_id):
    try:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM FoodItem WHERE food_id = %s", (food_id,))
                conn.commit()
                if cur.rowcount == 0:
                    return jsonify({'success': False, 'error': 'Donation not found'}), 404
            return jsonify({'success': True, 'message': 'Donation deleted successfully!'})
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/donors', methods=['GET'])
def get_all_donors():
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT d.*, z.zone_name, z.city
                FROM Donor d JOIN Zone z ON d.zone_id = z.zone_id
                ORDER BY d.donor_name
            """)
            donors = cur.fetchall()
        conn.close()
        return jsonify({'success': True, 'data': serialize_rows(donors)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════
# RECEIVER ROUTES
# ═══════════════════════════════════════════════════════════

@app.route('/api/add_receiver', methods=['POST'])
def add_receiver():
    try:
        data = request.get_json()
        required = ['receiver_name', 'organization_name', 'phone', 'address', 'zone_id']
        for field in required:
            if field not in data or not data[field]:
                return jsonify({'success': False, 'error': f'Missing field: {field}'}), 400

        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO Receiver (receiver_name, organization_name, phone, address, zone_id)
                    VALUES (%s, %s, %s, %s, %s)
                """, (data['receiver_name'], data['organization_name'],
                      data['phone'], data['address'], data['zone_id']))
                conn.commit()
                receiver_id = cur.lastrowid
            return jsonify({'success': True, 'receiver_id': receiver_id,
                            'message': 'Receiver registered successfully!'})
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/available_food', methods=['GET'])
def available_food():
    try:
        zone_id = request.args.get('zone_id')
        category = request.args.get('category')

        conn = get_connection()
        with conn.cursor() as cur:
            query = """
                SELECT f.food_id, f.food_name, f.category, f.quantity, f.unit,
                       f.is_perishable, f.cooked_time, f.expiry_date, f.status,
                       f.zone_id, f.created_at,
                       z.zone_name, z.city,
                       d.donor_id, d.donor_name, d.phone AS donor_phone,
                       GetUrgencyLevel(f.expiry_date) AS urgency
                FROM FoodItem f
                JOIN Zone  z ON f.zone_id  = z.zone_id
                JOIN Donor d ON f.donor_id = d.donor_id
                WHERE f.status = 'available' AND f.expiry_date > NOW()
            """
            params = []
            if zone_id:
                query += " AND f.zone_id = %s"
                params.append(zone_id)
            if category:
                query += " AND f.category = %s"
                params.append(category)
            query += " ORDER BY f.expiry_date ASC"
            cur.execute(query, params)
            food = cur.fetchall()
        conn.close()
        return jsonify({'success': True, 'data': serialize_rows(food)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/food_categories', methods=['GET'])
def food_categories():
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT DISTINCT category FROM FoodItem ORDER BY category")
            cats = [row['category'] for row in cur.fetchall()]
        conn.close()
        return jsonify({'success': True, 'data': cats})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/request_food', methods=['POST'])
def request_food():
    try:
        data = request.get_json()
        required = ['receiver_id', 'food_id', 'requested_quantity']
        for field in required:
            if field not in data or not data[field]:
                return jsonify({'success': False, 'error': f'Missing field: {field}'}), 400

        conn = get_connection()
        try:
            with conn.cursor() as cur:
                # Check food is still available
                cur.execute("SELECT status, quantity FROM FoodItem WHERE food_id = %s", (data['food_id'],))
                food = cur.fetchone()
                if not food:
                    return jsonify({'success': False, 'error': 'Food item not found'}), 404
                if food['status'] != 'available':
                    return jsonify({'success': False, 'error': 'Food is no longer available'}), 409

                if float(data['requested_quantity']) > float(food['quantity']):
                    return jsonify({'success': False, 'error': 'Requested quantity exceeds available'}), 400

                # Insert request
                cur.execute("""
                    INSERT INTO Request (receiver_id, food_id, requested_quantity, request_status)
                    VALUES (%s, %s, %s, 'pending')
                """, (data['receiver_id'], data['food_id'], data['requested_quantity']))

                # Update food status
                cur.execute("UPDATE FoodItem SET status = 'requested' WHERE food_id = %s",
                            (data['food_id'],))

                conn.commit()
                request_id = cur.lastrowid
            return jsonify({'success': True, 'request_id': request_id,
                            'message': 'Food requested successfully!'})
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/receiver/<int:receiver_id>/requests', methods=['GET'])
def get_receiver_requests(receiver_id):
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT r.*, f.food_name, f.category, f.quantity AS available_quantity,
                       f.unit, f.expiry_date, f.status AS food_status,
                       d.donor_name,
                       z.zone_name, z.city,
                       GetUrgencyLevel(f.expiry_date) AS urgency
                FROM Request r
                JOIN FoodItem f  ON r.food_id     = f.food_id
                JOIN Donor    d  ON f.donor_id     = d.donor_id
                JOIN Zone     z  ON f.zone_id      = z.zone_id
                WHERE r.receiver_id = %s
                ORDER BY r.request_time DESC
            """, (receiver_id,))
            requests = cur.fetchall()
        conn.close()
        return jsonify({'success': True, 'data': serialize_rows(requests)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/request/<int:request_id>/status', methods=['PUT'])
def update_request_status(request_id):
    try:
        data = request.get_json()
        new_status = data.get('status')
        if new_status not in ('pending', 'approved', 'fulfilled', 'cancelled', 'expired'):
            return jsonify({'success': False, 'error': 'Invalid status'}), 400

        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("CALL UpdateDistributionStatus(%s, %s)",
                            (request_id, new_status))
                conn.commit()
            return jsonify({'success': True, 'message': f'Request status updated to {new_status}'})
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/receivers', methods=['GET'])
def get_all_receivers():
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT r.*, z.zone_name, z.city
                FROM Receiver r JOIN Zone z ON r.zone_id = z.zone_id
                ORDER BY r.receiver_name
            """)
            receivers = cur.fetchall()
        conn.close()
        return jsonify({'success': True, 'data': serialize_rows(receivers)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════
# ADMIN ROUTES
# ═══════════════════════════════════════════════════════════

@app.route('/api/dashboard_stats', methods=['GET'])
def dashboard_stats():
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            stats = {}
            cur.execute("SELECT COUNT(*) AS c FROM Donor")
            stats['total_donors'] = cur.fetchone()['c']

            cur.execute("SELECT COUNT(*) AS c FROM Receiver")
            stats['total_receivers'] = cur.fetchone()['c']

            cur.execute("SELECT COUNT(*) AS c FROM FoodItem WHERE status = 'available' AND expiry_date > NOW()")
            stats['available_donations'] = cur.fetchone()['c']

            cur.execute("SELECT COUNT(*) AS c FROM Request WHERE request_status = 'fulfilled'")
            stats['fulfilled_requests'] = cur.fetchone()['c']

            cur.execute("SELECT COUNT(*) AS c FROM FoodItem WHERE status = 'expired' OR expiry_date <= NOW()")
            stats['expired_food'] = cur.fetchone()['c']

            cur.execute("SELECT COUNT(*) AS c FROM Request WHERE request_status = 'pending'")
            stats['pending_requests'] = cur.fetchone()['c']

            cur.execute("SELECT COUNT(*) AS c FROM FoodItem")
            stats['total_food_items'] = cur.fetchone()['c']

            cur.execute("SELECT COUNT(*) AS c FROM Request")
            stats['total_requests'] = cur.fetchone()['c']

        conn.close()
        return jsonify({'success': True, 'data': stats})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/expired_food', methods=['GET'])
def expired_food():
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT f.*, d.donor_name, z.zone_name, z.city
                FROM FoodItem f
                JOIN Donor d ON f.donor_id = d.donor_id
                JOIN Zone  z ON f.zone_id  = z.zone_id
                WHERE f.status = 'expired' OR f.expiry_date <= NOW()
                ORDER BY f.expiry_date DESC
            """)
            food = cur.fetchall()
        conn.close()
        return jsonify({'success': True, 'data': serialize_rows(food)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/zone_report', methods=['GET'])
def zone_report():
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    z.zone_id,
                    z.zone_name,
                    z.city,
                    COUNT(DISTINCT d.donor_id)    AS donor_count,
                    COUNT(DISTINCT rec.receiver_id) AS receiver_count,
                    COUNT(DISTINCT CASE WHEN f.status = 'available' AND f.expiry_date > NOW()
                                        THEN f.food_id END) AS available_food,
                    COUNT(DISTINCT CASE WHEN f.status = 'fulfilled'
                                        THEN f.food_id END) AS fulfilled_food,
                    COUNT(DISTINCT CASE WHEN f.status = 'expired' OR f.expiry_date <= NOW()
                                        THEN f.food_id END) AS expired_food
                FROM Zone z
                LEFT JOIN Donor    d   ON z.zone_id = d.zone_id
                LEFT JOIN Receiver rec ON z.zone_id = rec.zone_id
                LEFT JOIN FoodItem f   ON z.zone_id = f.zone_id
                GROUP BY z.zone_id, z.zone_name, z.city
                ORDER BY z.zone_name
            """)
            report = cur.fetchall()
        conn.close()
        return jsonify({'success': True, 'data': serialize_rows(report)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/monthly_report', methods=['GET'])
def monthly_report():
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    DATE_FORMAT(created_at, '%%Y-%%m') AS month,
                    COUNT(*) AS total_donations,
                    SUM(CASE WHEN status = 'fulfilled' THEN 1 ELSE 0 END) AS fulfilled,
                    SUM(CASE WHEN status = 'expired' THEN 1 ELSE 0 END) AS expired,
                    SUM(CASE WHEN status = 'available' THEN 1 ELSE 0 END) AS available
                FROM FoodItem
                GROUP BY DATE_FORMAT(created_at, '%%Y-%%m')
                ORDER BY month DESC
                LIMIT 12
            """)
            report = cur.fetchall()
        conn.close()
        return jsonify({'success': True, 'data': serialize_rows(report)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/audit_log', methods=['GET'])
def get_audit_log():
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT * FROM AuditLog
                ORDER BY changed_at DESC
                LIMIT 50
            """)
            logs = cur.fetchall()
        conn.close()
        return jsonify({'success': True, 'data': serialize_rows(logs)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════
# RUN
# ═══════════════════════════════════════════════════════════

if __name__ == '__main__':
    app.run(debug=True, port=5000)
