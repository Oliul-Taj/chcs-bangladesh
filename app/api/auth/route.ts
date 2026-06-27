import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const { identity } = await request.json();
    const cleanId = identity.trim();

    if (!cleanId) {
      return NextResponse.json({ error: "Identifier is required" }, { status: 400 });
    }

    // Smart Matching Layout using exact conditions matching your CSV definitions
    if (cleanId === "1988102938475") {
      return NextResponse.json({
        type: 'NID',
        redirect: '/patient?id=1988102938475',
        name: 'Fahmida Begum'
      });
    } 
    
    if (cleanId === "2012582910294") {
      return NextResponse.json({
        type: 'BC',
        redirect: '/patient?id=2012582910294',
        name: 'Tasnim Ara (Minor)'
      });
    }

    if (cleanId.toUpperCase() === "EB-007") {
      return NextResponse.json({
        type: 'PASSPORT',
        redirect: '/patient?id=EB-007',
        name: 'Foreign National Profile'
      });
    }

    // Default Fallback
    return NextResponse.json({ error: "Identifier profile record not found in system datasets." }, { status: 404 });
  } catch (err) {
    return NextResponse.json({ error: "Internal System Server Error" }, { status: 500 });
  }
}
