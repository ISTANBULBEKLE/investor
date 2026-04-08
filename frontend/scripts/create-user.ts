/**
 * Creates the admin user for the INVESTOR app.
 *
 * Usage:
 *   npx tsx scripts/create-user.ts
 *
 * This calls the better-auth sign-up endpoint directly.
 * Run this once after first setup.
 */

const BASE_URL = process.env.BETTER_AUTH_URL || "http://localhost:3000";

async function createUser() {
  const email = process.argv[2] || "admin@investor.local";
  const password = process.argv[3] || "admin123";
  const name = process.argv[4] || "Admin";

  console.log(`Creating user: ${email}`);

  const res = await fetch(`${BASE_URL}/api/auth/sign-up/email`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Origin": BASE_URL,
    },
    body: JSON.stringify({ email, password, name }),
  });

  if (res.ok) {
    const data = await res.json();
    console.log("User created successfully!");
    console.log(`  Email: ${email}`);
    console.log(`  Name: ${name}`);
    console.log(`  ID: ${data.user?.id || data.id || "created"}`);
  } else {
    const error = await res.text();
    console.error(`Failed to create user: ${res.status}`);
    console.error(error);
  }
}

createUser().catch(console.error);
