# 🧾 Nuvamed — Customer Signup & NPI Form Integration

## 📌 Overview

This project extends the **Shopify customer registration process** to validate and control access for **clinics and verified healthcare providers** using their **NPI (National Provider Identifier)**.  
The objective is to ensure that only legitimate, approved medical entities can register, view pricing, and make purchases on the Nuvamed platform.

---

## 🧩 Investigation

While integrating the NPI validation and custom signup flow within **Shopify’s New Customer Accounts**, several key issues were identified:

1. **JavaScript Event Isolation**
   - The `submit` event listeners were not triggering as expected.
   - Shopify’s new authentication pages use a **sandboxed, iframe-based architecture** that blocks custom JavaScript execution on forms.

2. **Dynamic DOM Limitations**
   - The `<form>` element was rendered dynamically, often **after** the JS executed.
   - As a result, standard `document.querySelector()` or `addEventListener()` calls failed to bind correctly.

3. **Restricted Customization in New Customer Accounts**
   - Shopify no longer allows direct modification of `/authentication/login` or related templates.
   - This prevents developers from injecting validation logic or additional fields (like NPI) directly into the default signup process.

4. **Limited Documentation & Community Knowledge**
   - Even experienced Shopify developers often **lack deep insight into the new hosted account system**, since it operates outside the theme layer.
   - Most guides and tutorials online still reference **Classic Accounts**, which behave differently.

> 🧠 **Conclusion:**  
> These constraints make implementing advanced form logic (like real-time NPI verification) within Shopify’s hosted account system technically **impossible without external integration**.

---

## 🧭 Solution We Are Moving Forward With

Given Shopify’s technical restrictions, we are moving forward with a **hybrid solution** that integrates a **custom clinic signup form** and a **FastAPI backend validation service**.

### 🔧 Architecture Summary

- **Frontend:** Custom Liquid + JS form hosted in Shopify (under `/pages/clinic-signup`).
- **Backend:** FastAPI service handling NPI validation and pre-registration checks.

### 💡 Why This Approach

- The custom form gives us **full control** over input fields and validation logic.
- FastAPI enables **real-time NPI validation** before account creation.
- Singleton acts as an **access control bridge** until the full custom logic replaces it (Phase 2).

The system is being developed in **two main phases**:

---

## ⚠️ Current Limitations (New Customer Accounts)

| Feature | Classic Accounts | New Accounts |
|----------|-----------------|---------------|
| Editable templates | ✅ | ❌ |
| Custom JS injection | ✅ | ❌ |
| Themed layout customization | ✅ | ⚠️ Limited |
| Native API access | ✅ | ⚠️ Restricted |
| Hosted by | Theme | Shopify |

As a result, it is **not currently possible** to:

- Inject custom validation scripts inside `/authentication/login`.
- Add NPI fields directly into the hosted signup form.

Hence the decision to **offload registration to a custom page** with controlled logic and design.

---

## 🚀 Phase 1 — Temporary Solution (✅ Implemented)

### 🧩 App Used: *Singleton Verify Customers*

This phase leverages the third-party app **[Singleton Verify Customers](https://apps.shopify.com/verify-customers)** as an initial access control mechanism.

> 💸 **Note:** The Singleton app has a cost of **$20 USD per month**.  
> It is being used as a temporary measure until the custom verification and access control system is fully developed and deployed.

### 🔧 How It Works

- When a user signs up via the Shopify-hosted registration page, the account is created **but remains unapproved**.
- A **manual approval checkbox** (`Approve Customer`) is available in the Shopify admin panel.
- Until the customer is approved:
  - They **cannot see prices**.
  - They **cannot add products to cart**.
  - They **cannot complete purchases**.
- Only after an internal team member verifies and approves the account will the customer gain full access.

### 🧠 Internal Review Process

- Internal users have access to a **private verification page**.
- This page includes an **NPI lookup integration**, allowing staff to cross-check the customer’s information against the **official NPI Registry**.
- The verification ensures that **only legitimate providers** are granted full access.

### ⚙️ Purpose of This Phase

This solution serves as a **controlled access layer** while the permanent, fully automated signup validation system is being developed (see Phase 2).

---

## 🔮 Phase 2 — Final Implementation (In Progress)

### 🧩 Goal

Develop a **custom registration form** (outside of Shopify’s hosted login/signup flow) that directly integrates with:

- The **NPI Registry API** for real-time validation.
- Shopify’s customer account creation endpoint (or a backend proxy API).
- Custom business logic for approval, notifications, and conditional access.

### 🧱 Core Components

1. **Custom Frontend Form (Shopify Page or App Embed)**
   - Fields:
     - Clinic Name  
     - Contact Name  
     - Email  
     - NPI Number  
     - Phone  
     - Address  
     - Additional metadata if required
   - Performs **real-time NPI validation**.

2. **JavaScript Behavior**
   - Input validation (frontend).
   - Dynamic floating labels for UX.
   - Handles form submission via `fetch()`.
   - Displays success/error states.

3. **Backend (FastAPI)**
   - Proxy endpoint `/check-npi` for secure validation against `https://npiregistry.cms.hhs.gov/api/`.
   - Implements:
     - CORS
     - Rate limiting
     - Request timeouts
     - Security headers
   - Returns a simplified JSON response with provider info.

4. **Shopify Integration**
   - Currently limited due to **New Customer Accounts** restrictions (Shopify-managed, not editable).
   - Custom signup form hosted on a dedicated page (e.g., `/pages/clinic-signup`).
   - Will eventually replace the Singleton Verify Customers workflow once validated.

---

## 🪜 Implementation Roadmap

| Step | Description | Status |
|------|--------------|--------|
| 1 | Implement Singleton Verify Customers for access control | ✅ Done |
| 2 | Create internal NPI verification page | ✅ Done |
| 3 | Develop FastAPI `/check-npi` proxy service | ✅ Done |
| 4 | Build standalone clinic signup page (Liquid + JS) | 🟡 In progress |
| 5 | Add direct validation before submission | 🟡 In progress |
| 6 | Implement complete FastAPI server hardening (security headers, rate limit, timeouts, CORS rules) | 🔜 Planned |
| 7 | Deprecate Singleton app once full custom signup system is live (removes $20/mo cost) | 🔜 Planned |

---

## 🧠 Security & Validation

The **FastAPI service** includes key security features such as:

- Strict CORS configuration.
- Rate limiting and request timeouts.  
- Secure headers for anti-DDoS protection.  

> ⚠️ **Note:** These components are currently under **active development** and will be finalized in Step 6 of the roadmap.

Additional measures:

- NPI validation occurs **before** registration or account creation.  
- Only verified clinics can proceed to checkout after internal approval.  
- Final deployment will include improved logging, request auditing, and protection against brute-force or spam attacks.

---

## 🧭 Client Decisions Needed

Before proceeding with full deployment, several points require input from the **Nuvamed team**:

| Decision Area | Description | Required Action |
|----------------|--------------|-----------------|
| 🏗️ **Hosting Provider** | Decide whether to host FastAPI on **Railway** (recommended for setup speed) or migrate later to **Nuvamed’s internal infrastructure**. | ✅ Confirm hosting strategy |
| 📧 **Support Email** | Define the email address used to notify or assist users whose NPI verification fails. | ✅ Provide contact email |
| 👥 **Legacy Accounts** | Determine what to do with **existing customer accounts created before approval logic** (e.g., auto-disable, contact manually, or flag for review). | ✅ Confirm remediation plan |

---

## 📚 References

- [Shopify Docs — Customer Accounts](https://help.shopify.com/en/manual/customers/customer-accounts)
- [NPI Registry API](https://npiregistry.cms.hhs.gov/)
- [Singleton Verify Customers App](https://apps.shopify.com/b2b-verify-customers)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Demo Video](https://www.loom.com/share/678c17195be44497a0ef4a36eec6387e?sid=60b56480-cb4e-4552-b5a8-3261d4a224b3)

---
